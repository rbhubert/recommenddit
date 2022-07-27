from information_recovery.data_collection_to_excel import collect_subreddits, close_file

"""
    Retrieve information and posts from subreddits, and save the data in an excel file.
"""
if __name__ == '__main__':
    collect_subreddits(subreddits=["pokemon"])
    close_file()
