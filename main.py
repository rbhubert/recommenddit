from information_recovery.data_collection_to_excel import collect_subreddits

"""
    Retrieve information and posts from subreddits, and save the data in an excel file.
"""
if __name__ == '__main__':
    collect_subreddits(subreddits=["nottheonion",
                                   "sports",
                                   "Documentaries",
                                   "memes",
                                   "dataisbeautiful",
                                   "UpliftingNews",
                                   "photoshopbattles",
                                   "listentothis",
                                   "history",
                                   "philosophy",
                                   "Futurology",
                                   "television",
                                   "OldSchoolCool",
                                   "personalfinance",
                                   "InternetIsBeautiful",
                                   "WritingPrompts",
                                   "creepy"])
