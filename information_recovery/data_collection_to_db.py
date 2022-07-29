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


"""
    Example of collecting information from the subreddits in the list
"""

# while True:
#     subreddits_to_explore = get_subreddits_to_explore()
#     if not subreddits_to_explore:
#         break
#     collect_subreddits(subreddits=subreddits_to_explore)
#

collect_subreddits(subreddits=["lifehacks", "NatureIsFuckingLit", "oddlysatisfying", "Unexpected",
                               "relationship_advice", "WTF", "Minecraft"])
