import os
import time

import praw
import prawcore
from dotenv import load_dotenv
from praw.models import MoreComments

from database.subreddit import Subreddit, RedditSubmission, RedditComment, CrossPost

"""
    Loading environment variables
    with load_dotenv()
"""
load_dotenv()

"""
    Connecting with reddit through praw,
    using the environment variables defined in .env
"""
user_agent = os.getenv("USERAGENT")
reddit_client = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=user_agent,
)


def post_type(submission) -> str:
    """
    Determines the type of the submission/post. Can be "image", "gallery", "video", "poll", "text" or "link".

    :param submission: the information of the submission.
    :return: a str representing the type of the post.
    """
    if getattr(submission, "post_hint", "") == "image":
        return "image"
    elif getattr(submission, "is_gallery", False):
        return "gallery"
    elif submission.is_video:
        return "video"
    elif hasattr(submission, "poll_data"):
        return "poll"
    elif submission.is_self:
        return "text"
    return "link"


def create_submission(submission):
    """
    Creates an instance of RedditSubmission using the information of the submission/post.

    :param submission: the information about the submission.
    :return: an instance of RedditSubmission
    """
    subreddit_name = submission.subreddit.display_name

    # Avoiding crossposts to profiles.
    if subreddit_name.startswith("u_") or subreddit_name.startswith("u/"):
        return None

    author = submission.author.name if submission.author else "None"
    comments = collect_comments(submission)
    p_type = post_type(submission)
    video_duration = 0

    if submission.is_video:
        if submission.media:
            video_duration = submission.media["reddit_video"]["duration"]

    post = RedditSubmission(post_id=submission.id,
                            title=submission.title,
                            author=author,
                            date_created=submission.created_utc,
                            nsfw=submission.over_18,
                            comments=comments,
                            post_type=p_type,
                            upvote_ratio=submission.upvote_ratio,
                            total_awards=submission.total_awards_received,
                            num_crossposts=submission.num_crossposts,
                            text=submission.selftext,
                            video_duration=video_duration,
                            category=submission.link_flair_text,
                            subreddit=submission.subreddit.display_name)
    return post


def collect_submissions(subreddit: str, last_submission: [str, int] = None,
                        submissions_limit: int = 350, crossposts_limit: int = 10):
    """
    Goes through each submission in the subreddit, obtaining also all the comments for each submission.
    We also get the information of the subreddit.

    :param subreddit: a str representing the name of a subreddit.
    :param last_submission: a [str, int] representing the id of the last_submission retrieved for that subreddit and the offset/number of submissions already processed.
    :param submissions_limit: an integer between 1 and 1000 representing the number of submissions to be retrieved for the subreddit. Default value=350
    :param crossposts_limit: an integer between 1 and 1000 representing the number of crossposts to be retrieved for each submission. Default value=3
    :return:
        - subreddit_info: a Subreddit instance with the information of the subreddit.
        - submissions: a list of RedditSubmission's with the information of each submission.
        - crossposts: a list of CrossPost's of each found crossposts.
    """
    # todo Add related subreddits to each subreddit. This vary between subreddits

    if last_submission:
        submissions_limit = submissions_limit - last_submission[1]
        last_submission = last_submission[0] if last_submission[0] else ""
    else:
        last_submission = ""

    subreddit_info = None
    submissions = []
    crossposts = []

    last_exception = None
    timeout = 900  # seconds = 15 minutes
    time_start = int(time.time())
    number_submissions_retrieved = 0

    while (number_submissions_retrieved < submissions_limit) and int(time.time()) < time_start + timeout:
        try:
            params = {"after": last_submission} if last_submission else {}

            for submission in reddit_client.subreddit(subreddit).top(limit=submissions_limit,
                                                                     params=params):
                # limit=None get all the possible posts
                print(f"\t [{subreddit}] Collecting submission {submission.id}.")

                # Getting the information of the Subreddit only the first time we get a submission
                if not number_submissions_retrieved:
                    subreddit_info = Subreddit(name=submission.subreddit.display_name,
                                               description=submission.subreddit.public_description,
                                               date_created=submission.subreddit.created_utc,
                                               nsfw=submission.subreddit.over18,
                                               subscribers=submission.subreddit.subscribers)

                # Obtaining the information of the submission
                post = create_submission(submission)

                if not post:
                    continue

                submissions.append(post)

                number_submissions_retrieved += 1
                last_submission = "t3_" + post.id

                # If the post does not have crossposts
                if submission.num_crossposts == 0:
                    continue

                # We also get the post for each crosspost --- limit = 10
                for duplicate in submission.duplicates(limit=crossposts_limit):

                    # Avoiding crossposts to profiles.
                    if duplicate.subreddit.display_name.startswith(("u_", "u/")):
                        return None

                    print(f"\t [{subreddit}] Collecting crosspost.")

                    post_dup = create_submission(duplicate)
                    submissions.append(post_dup)

                    crosspost = CrossPost(parent_id=post.id, post_id=post_dup.id)
                    crossposts.append(crosspost)

        except prawcore.exceptions.ServerError as e:
            # wait for 30 seconds since sending more requests to overloaded server might not be helping
            last_exception = e
            print("### Server error - Waiting a minute before trying again ###")
            time.sleep(30)
        except prawcore.exceptions.RequestException as e:
            # exception is related with internet connection
            last_exception = e
            print("### Connection error - Waiting two minutes before trying again ###")
            time.sleep(120)

    if number_submissions_retrieved != submissions_limit:
        print(f"### We weren't able to collect all {submissions_limit} submissions for {subreddit} subreddit. ###")
        print(" ### Please try again. ###")
        raise last_exception

    return subreddit_info, submissions, crossposts


def collect_comments(submission):
    """
    Goes through each comment in the submission and creates instances of RedditComment with the comment information.

    :param submission: the submission information
    :return: a list of RedditComment's.
    """
    comments = []

    print("\t\t Collecting comments.")
    submission.comment_sort = "top"

    for comment in submission.comments:
        if isinstance(comment, MoreComments):
            continue

        sum_up_down = comment.ups + comment.downs
        score = comment.ups / sum_up_down if sum_up_down else 0
        author = comment.author.name if comment.author else "None"

        submission_id = comment.parent_id if "submission_id" not in vars(comment).keys() else comment.submission_id
        comm = RedditComment(comment_id=comment.id, text=comment.body, author=author,
                             date_created=comment.created_utc, parent_id=comment.parent_id,
                             submission_id=submission_id.replace("t3_", ""), upvote_ratio=score,
                             pinned=comment.stickied)
        comments.append(comm)

    return comments
