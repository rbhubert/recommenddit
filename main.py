from information_recovery.data_collection_to_excel import collect_subreddits

"""
    Example: retrieve information and posts from subreddit 'funny', and save the data in 4 excels files:
    data/subreddits.csv, data/submissions.csv, data/comments.csv and data/crossposts.csv.
"""
if __name__ == '__main__':
    collect_subreddits(subreddits=["funny"])
