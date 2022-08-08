import os
from enum import Enum

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

from utils.singleton import Singleton

"""
    Loading the environment variables
    through load_dotevn()
"""
load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT")


class RedditTables(Enum):
    SUBREDDITS = "subreddit"
    SUBMISSIONS = "submission"
    CROSSPOSTS = "crosspost"
    COMMENTS = "reddit_replies"


class Database(metaclass=Singleton):
    """
        Class for database connection. This class is a Singleton.
    """

    def __init__(self):
        self.db_conn = psycopg2.connect(database=DATABASE_NAME,
                                        host=DATABASE_HOST,
                                        user=DATABASE_USER,
                                        password=DATABASE_PASSWORD,
                                        port=DATABASE_PORT)
        self.db_conn.autocommit = True
        self.cursor = self.db_conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_conn.close()

    def get_info(self, select_columns, condition_from, condition_where=None):
        sql_statement = f"SELECT {select_columns} FROM {condition_from}"
        if condition_where:
            sql_statement += f" WHERE {condition_where}"
        sql_statement += ";"

        self.cursor.execute(sql_statement)

        # Retrieve query results
        records = self.cursor.fetchall()
        return records

    def add_info(self, table: str, columns: str, values: [str]):
        """
        Makes a INSERT query in the database.
        """
        insert_query = f"""INSERT INTO {table} ({columns}) values %s ON CONFLICT DO NOTHING;"""
        execute_values(self.cursor, insert_query, values)

    def get_subreddit_info(self, subreddit_name):
        table = RedditTables.SUBREDDITS.value
        pass

    def save_subreddits(self, subreddits: ["Subreddit"]):
        """
        Saves the subreddit information in the database.
        """
        table = RedditTables.SUBREDDITS.value
        columns = "name, description, date_created, nsfw, subscribers"
        values = [(subreddit.name, subreddit.description, subreddit.date_created, subreddit.nsfw,
                   subreddit.subscribers)
                  for subreddit in subreddits]
        return self.add_info(table=table, columns=columns, values=values)

    def save_submissions(self, submissions: ["RedditSubmission"]):
        """
        Saves a list of submissions in the database.
        """
        table = RedditTables.SUBMISSIONS.value
        columns = "post_id, title, author, date_created, nsfw, post_type, upvote_ratio, " \
                  "total_awards, num_crossposts, post_content, video_duration, category,subreddit"
        values = [(submission.id, submission.title, submission.author, submission.date_created, submission.nsfw,
                   submission.post_type, submission.upvote_ratio, submission.total_awards, submission.num_crossposts,
                   submission.text, submission.video_duration, submission.category, submission.subreddit)
                  for submission in submissions]
        return self.add_info(table=table, columns=columns, values=values)

    def save_crossposts(self, crossposts: ["CrossPost"]):
        """
        Saves a list of crossposts in the database.
        """
        table = RedditTables.CROSSPOSTS.value
        columns = "crosspost_parent_id, crosspost_id"
        values = [(crosspost.crosspost_parent_id, crosspost.post_id) for crosspost in crossposts]
        return self.add_info(table=table, columns=columns, values=values)

    def save_comments(self, comments: ["RedditComment"]):
        """
        Saves a list of comments in the database.
        """
        table = RedditTables.COMMENTS.value
        columns = "comment_id, comment_content, author, date_created, parent_id, submission_id, upvote_ratio, pinned"
        values = [(comment.id, comment.text, comment.author, comment.date_created, comment.parent_id,
                   comment.submission_id, comment.upvote_ratio, comment.pinned) for comment in comments]
        return self.add_info(table=table, columns=columns, values=values)

    def get_unsaved_subreddits(self):
        """
        Makes a SELECT query to get all the subreddits found in the database that do not have an entry in the subreddit
        table.
        """
        sql_select = """
                    SELECT DISTINCT submission.subreddit FROM submission
                    LEFT OUTER JOIN subreddit
                    ON (submission.subreddit = subreddit.name)
                    WHERE subreddit.name IS NULL;
                    """
        self.cursor.execute(sql_select)

        # Retrieve query results
        records = self.cursor.fetchall()
        return records


database = Database()
