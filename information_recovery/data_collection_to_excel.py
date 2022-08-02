import csv

from information_recovery.reddit_connection import collect_submissions

subreddits_file = "data/subreddits.csv"
submissions_file = "data/submissions.csv"
comments_file = "data/comments.csv"
crossposts_file = "data/crossposts.csv"


def add_subreddits(subreddit):
    with open(subreddits_file, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        entry = (subreddit.name, subreddit.description, subreddit.date_created, subreddit.nsfw, subreddit.subscribers)
        writer.writerow(entry)


def add_submissions(submissions):
    submissions_entries = []
    for submission in submissions:
        entry = (submission.id, submission.title, submission.author, submission.date_created, submission.nsfw,
                 submission.post_type, submission.upvote_ratio, submission.total_awards, submission.num_crossposts,
                 submission.text, submission.video_duration, submission.category, submission.subreddit)
        submissions_entries.append(entry)
        add_comments(submission.comments)

    with open(submissions_file, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(submissions_entries)


def add_comments(comments):
    comments_entries = []
    for comment in comments:
        entry = (comment.id, comment.text, comment.author, comment.date_created, comment.parent_id,
                 comment.submission_id, comment.upvote_ratio, comment.pinned)
        comments_entries.append(entry)

    with open(comments_file, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(comments_entries)


def add_crossposts(crossposts):
    crossposts_entries = []
    for crosspost in crossposts:
        entry = (crosspost.crosspost_parent_id, crosspost.post_id)
        crossposts_entries.append(entry)

    with open(crossposts_file, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(crossposts_entries)


def collect_subreddits(subreddits: [str]):
    """
    Go through the list of subreddits collecting all the submissions, crossposts and comments, and them save them
    in an excel (in batch).
    :param subreddits: list of str representing subreddits. Can be null.
    """

    for subreddit in subreddits:
        print(f"Getting posts from subreddit: '{subreddit}'.")

        subreddit_info, submissions, crossposts = collect_submissions(subreddit)

        # Update Excel
        add_subreddits(subreddit_info)
        add_submissions(submissions)
        add_crossposts(crossposts)

        print(f"\t Saving information of subreddit: '{subreddit}'.")
