import csv

from database.database import database
from database.subreddit import Subreddit, RedditSubmission, RedditComment, CrossPost
from information_recovery.reddit_connection import collect_submissions

csv_folder = "data/"
to_db_folder = "data/to_db/"

subreddits_file = "subreddits.csv"
submissions_file = "submissions.csv"
comments_file = "comments.csv"
crossposts_file = "crossposts.csv"


def add_subreddits(subreddit):
    with open(csv_folder + subreddits_file, "a", encoding="utf-8", newline="") as file:
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

    with open(csv_folder + submissions_file, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(submissions_entries)


def add_comments(comments):
    comments_entries = []
    for comment in comments:
        entry = (comment.id, comment.text, comment.author, comment.date_created, comment.parent_id,
                 comment.submission_id, comment.upvote_ratio, comment.pinned)
        comments_entries.append(entry)

    with open(csv_folder + comments_file, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(comments_entries)


def add_crossposts(crossposts):
    crossposts_entries = []
    for crosspost in crossposts:
        entry = (crosspost.crosspost_parent_id, crosspost.post_id)
        crossposts_entries.append(entry)

    with open(csv_folder + crossposts_file, "a", encoding="utf-8", newline="") as file:
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


def save_subreddits():
    subreddits = []

    print("Subreddits")
    print("\n Reading csv file")
    with open(to_db_folder + subreddits_file, newline="", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            subreddits.append(Subreddit(name=row[0],
                                        description=row[1],
                                        date_created=row[2],
                                        nsfw=bool(row[3]),
                                        subscribers=int(row[4])))

    print("\n Saving in db")
    database.save_subreddits(subreddits=subreddits)


def save_submissions():
    submissions = []

    print("Submissions")
    print("\n Reading csv file")
    with open(to_db_folder + submissions_file, newline="", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            submissions.append(RedditSubmission(post_id=row[0],
                                                title=row[1],
                                                author=row[2],
                                                date_created=row[3],
                                                nsfw=bool(row[4]),
                                                comments=[],
                                                post_type=row[5],
                                                upvote_ratio=float(row[6]),
                                                total_awards=int(row[7]),
                                                num_crossposts=int(row[8]),
                                                text=row[9],
                                                video_duration=int(row[10]) if row[10] else None,
                                                category=row[11],
                                                subreddit=row[12]))
    print("\n Saving in db")
    database.save_submissions(submissions=submissions)


def save_comments():
    comments = []

    print("Comments")
    print("\n Reading csv file")
    with open(to_db_folder + comments_file, newline="", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            comments.append(RedditComment(comment_id=row[0],
                                          text=row[1],
                                          author=row[2],
                                          date_created=row[3],
                                          parent_id=row[4],
                                          submission_id=row[5],
                                          upvote_ratio=float(row[6]),
                                          pinned=bool(row[7])))

    print("\n Saving in db")
    database.save_comments(comments=comments)


def save_crossposts():
    crossposts = []

    print("Crossposts")
    print("\n Reading csv file")
    with open(to_db_folder + crossposts_file, newline="", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            crossposts.append(CrossPost(parent_id=row[0], post_id=row[1]))

    print("\n Saving in db")
    database.save_crossposts(crossposts=crossposts)


def csv_file_to_db():
    print(" -- Start reading csv and saving in db --")
    save_subreddits()
    save_submissions()
    save_comments()
    save_crossposts()
    print(" -- Finish --")
