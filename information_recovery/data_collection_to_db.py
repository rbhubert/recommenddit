from database.database import database
from information_recovery.reddit_connection import collect_submissions


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

        try:
            print(f"Getting posts from subreddit: '{subreddit}'.")

            subreddit_info, submissions, crossposts = collect_submissions(subreddit)
            comments = []
            for subm in submissions:
                comments.extend(subm.comments)

            # Update Database
            database.save_subreddit(subreddit=[subreddit_info])
            database.save_submissions(submissions=submissions)
            database.save_comments(comments=comments)
            database.save_crossposts(crossposts=crossposts)

            print(f"\t Saving information of subreddit: '{subreddit}'.")
        except Exception:
            print("----- Ending program execution not to happily :c -----")
            break


def complete_collection():
    """
    todo
    """

    subreddits_records = database.get_uncompleted_subreddits(min_submissions=350)

    for row in subreddits_records:
        subreddit = row[0]
        post_id = row[1]
        offset = row[2]

        try:
            print(f"Getting posts from subreddit: '{subreddit}'.")

            subreddit_info, submissions, crossposts = collect_submissions(subreddit=subreddit,
                                                                          last_submission=[post_id, offset])

            comments = []
            for subm in submissions:
                comments.extend(subm.comments)

            # Update Database
            database.save_subreddit(subreddit=[subreddit_info])
            database.save_submissions(submissions=submissions)
            database.save_comments(comments=comments)
            database.save_crossposts(crossposts=crossposts)

            print(f"\t Saving information of subreddit: '{subreddit}'.")
        except Exception:
            print("----- Ending program execution not to happily :c -----")
            break
