import csv

from database.database import database
from database.subreddit import Subreddit, RedditSubmission, RedditComment, CrossPost
from information_recovery.reddit_connection import collect_submissions
import os

csv_folder = "data/"

subreddits_file = csv_folder + "subreddits.csv"
submissions_file = csv_folder + "submissions.csv"
comments_file = csv_folder + "comments.csv"
crossposts_file = csv_folder + "crossposts.csv"


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


def _helper_get_index_last_subreddit_in_csv(subreddits_list):
    if not os.path.exists(subreddits_file):
        return -1, None

    with open(subreddits_file, "r", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        rows = list(csv_reader)
        subreddit = rows[-1][0] if rows else None  # last row, first column

    if not subreddit:
        return -1, None

    try:
        idx_subreddit = subreddits_list.index(subreddit)

        if not os.path.exists(submissions_file):
            return idx_subreddit, None

        with open(submissions_file, "r", encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            rows = list(csv_reader)

            offset = 0
            i = -1
            last_submission = None
            while ((i + len(rows)) > 0) and offset != 350:
                if rows[i][-1] == subreddit:
                    offset += 1
                    if not last_submission:
                        last_submission = rows[i]
                i -= 1

        post_id = "t3_" + last_submission[0] if last_submission else None
        return idx_subreddit, [post_id, offset]
    except ValueError:
        return -1, None


def collect_subreddits(subreddits: [str]):
    """
    Go through the list of subreddits collecting all the submissions, crossposts and comments, and them save them
    in an Excel (in batch).

    :param subreddits: list of str representing subreddits. Can be null.
    """

    # Getting last subreddit analyzed, and checking if it is part of the list,
    # If it is, we chop the list, so we don't include subreddits that we already analyzed
    # This is only in terms of _order_ of the list passed by argument, we don't check
    # each of the element in the list
    idx_last_subreddit, last_submission_n_offset = _helper_get_index_last_subreddit_in_csv(subreddits_list=subreddits)
    if idx_last_subreddit > -1:
        subreddits = subreddits[idx_last_subreddit + 1:] if not last_submission_n_offset else subreddits[
                                                                                              idx_last_subreddit:]

    for subreddit in subreddits:
        print(f"Getting posts from subreddit: '{subreddit}'.")

        try:
            subreddit_info, submissions, crossposts = collect_submissions(subreddit=subreddit,
                                                                          last_submission=last_submission_n_offset)

            # Update Excel
            add_subreddits(subreddit_info)
            add_submissions(submissions)
            add_crossposts(crossposts)

            print(f"\t Saving information of subreddit: '{subreddit}'.")
        except Exception as e:
            print(e)
            print("----- Ending program execution not to happily :c -----")
            break


def complete_collection(file: str):
    """
    Given a file containing a list of tuples (subreddit_name, last_id, number_of_posts_retrieved) this function will
    gather top posts (comments, and crossposts) for each subreddit in the list with an offset of
    number_of_posts_retrieved to get up to submissions_limit (default: 350) posts.

    :param file: the file path where we have tuples (subreddit-name, last_id, offset) in each line
    """

    with open(file, "r", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        for row in csv_reader:
            subreddit = row[0]
            post_id = row[1]
            offset = int(row[2])

            try:
                print(f"Getting posts from subreddit: '{subreddit}'.")

                subreddit_info, submissions, crossposts = collect_submissions(subreddit=subreddit,
                                                                              last_submission=[post_id, offset])

                # Update Excel
                add_subreddits(subreddit_info)
                add_submissions(submissions)
                add_crossposts(crossposts)

                print(f"\t Saving information of subreddit: '{subreddit}'.")
            except Exception:
                print("----- Ending program execution not to happily :c -----")
                break


def save_subreddits():
    subreddits = []

    print("Subreddits")
    print("\t Reading csv file")
    with open(subreddits_file, newline="", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            subreddits.append(Subreddit(name=row[0],
                                        description=row[1],
                                        date_created=row[2],
                                        nsfw=bool(row[3]),
                                        subscribers=int(row[4])))
    print("\t Saving in db \n")
    database.save_subreddits(subreddits=subreddits)


def save_submissions():
    submissions = []

    print("Submissions")
    print("\t Reading csv file")
    with open(submissions_file, newline="", encoding="utf8") as csv_file:
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
    print("\t Saving in db \n")
    database.save_submissions(submissions=submissions)


def save_comments():
    comments = []

    print("Comments")
    print("\t Reading csv file")
    with open(comments_file, newline="", encoding="utf8") as csv_file:
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

    print("\t Saving in db \n")
    database.save_comments(comments=comments)


def save_crossposts():
    crossposts = []

    print("Crossposts")
    print("\t Reading csv file")
    with open(crossposts_file, newline="", encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            crossposts.append(CrossPost(parent_id=row[0], post_id=row[1]))

    print("\t Saving in db \n")
    database.save_crossposts(crossposts=crossposts)


def csv_file_to_db():
    print(" -- Start reading csv and saving in db -- \n")
    save_subreddits()
    save_submissions()
    save_comments()
    save_crossposts()
    print(" -- Finish -- \n")
