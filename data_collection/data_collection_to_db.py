import os
import time

import praw
import prawcore
from dotenv import load_dotenv
from praw.models import MoreComments

from database.database import database
from model.subreddit import Subreddit, RedditSubmission, RedditComment, CrossPost

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


def get_subreddits_to_explore():
    """
    Makes a call to the database to get all the subreddits that are not currently explored, but that were identified
    earlier in some crossposts.
    :return: a list of str representing subreddits names
    """
    subreddits_records = database.get_unsaved_subreddits()
    subreddits = [subred[0] for subred in subreddits_records]
    return subreddits


def collect_subreddits(subreddits: [str] = None):
    """
    Go through the list of subreddits collecting all the submissions, crossposts and comments, and them save them
    in the database (in batch).
    :param subreddits: list of str representing subreddits. Can be null.
    """

    if not subreddits:
        subreddits = get_subreddits_to_explore()

    for subreddit in subreddits:
        print(f"Getting posts from subreddit: '{subreddit}'.")

        subreddit_info, submissions, crossposts = collect_submissions(subreddit)
        comments = []
        for subm in submissions:
            comments.extend(subm.comments)

        # Update Database
        database.save_subreddit(subreddit=subreddit_info)
        database.save_submissions(submissions=submissions)
        database.save_crossposts(crossposts=crossposts)
        database.save_comments(comments=comments)
        print(f"\t Saving information of subreddit: '{subreddit}'.")


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
    :return: a instance of RedditSubmission
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


def collect_submissions(subreddit: str):
    """
    Goes through each submission in the subreddit, obtaining also all the comments for each submission.
    We also get the information of the subreddit.
    :param subreddit: a str representing the name of a subreddit.
    :return:
        - subreddit_info: a Subreddit instance with the information of the subreddit.
        - submissions: a list of RedditSubmission's with the information of each submission.
        - crossposts: a list of CrossPost's of each found crossposts.
    """

    first = True

    # todo Add related subreddits to each subreddit. This vary between subreddits

    subreddit_info = None
    submissions = []
    crossposts = []

    last_exception = None
    timeout = 900  # seconds = 15 minutes
    time_start = int(time.time())

    while not subreddit_info and int(time.time()) < time_start + timeout:
        try:
            for submission in reddit_client.subreddit(subreddit).top(limit=350):  # limit=None get all the possible
                # posts
                print(f"\t\t Collecting submission {submission.id}.")

                # Getting the information of the Subreddit
                if first:
                    subreddit_info = Subreddit(name=submission.subreddit.display_name,
                                               description=submission.subreddit.public_description,
                                               date_created=submission.subreddit.created_utc,
                                               nsfw=submission.subreddit.over18,
                                               subscribers=submission.subreddit.subscribers)
                    first = False

                # Obtaining the information of the submission
                post = create_submission(submission)
                submissions.append(post)

                # If the post does not have crossposts
                if submission.num_crossposts == 0:
                    continue

                # We also get the post for each crosspost.
                for duplicate in submission.duplicates():
                    post_dup = create_submission(duplicate)

                    if not post_dup:
                        continue

                    print(f"\t\t Collecting crosspost {post_dup.id}.")

                    submissions.append(post_dup)

                    crosspost = CrossPost(parent_id=post.id, post_id=post_dup.id)
                    crossposts.append(crosspost)

        except prawcore.exceptions.ServerError as e:
            # wait for 30 seconds since sending more requests to overloaded server might not be helping
            last_exception = e
            time.sleep(30)

    if not subreddit_info:
        raise last_exception

    return subreddit_info, submissions, crossposts


def collect_comments(submission):
    """
    Goes through each comment in the submission and creates instances of RedditComment with the comment information.
    :param submission: the submission informacion
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
                             submission_id=submission_id, upvote_ratio=score, pinned=comment.stickied)
        comments.append(comm)

    return comments

# Example of collecting information from the subreddits in the list

# while True:
#     subreddits_to_explore = get_subreddits_to_explore()
#     if not subreddits_to_explore:
#         break
#     collect_subreddits(subreddits=subreddits_to_explore)
#

# collect_subreddits(subreddits=["announcements"])
