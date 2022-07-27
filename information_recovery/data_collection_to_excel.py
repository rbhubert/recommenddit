import xlsxwriter

from information_recovery.reddit_connection import collect_submissions

workbook = xlsxwriter.Workbook("reddit_info.xlsx")
subreddits_worksheet = workbook.add_worksheet(name="subreddits")
submissions_worksheet = workbook.add_worksheet(name="submissions")
comments_worksheet = workbook.add_worksheet(name="comments")
crossposts_worksheet = workbook.add_worksheet(name="crossposts")

# Start from the first cell.
# Rows and columns are zero indexed.
subreddit_row = 0
submission_row = 0
comment_row = 0
crosspost_row = 0


def add_subreddit(subreddit):
    global subreddit_row

    subreddits_worksheet.write(subreddit_row, 0, subreddit.name)
    subreddits_worksheet.write(subreddit_row, 1, subreddit.description)
    subreddits_worksheet.write(subreddit_row, 2, subreddit.date_created)
    subreddits_worksheet.write(subreddit_row, 3, subreddit.nsfw)
    subreddits_worksheet.write(subreddit_row, 4, subreddit.subscribers)

    subreddit_row += 1


def add_submission(submission):
    global submission_row

    print("HI THERE")
    submissions_worksheet.write(submission_row, 0, submission.id)
    submissions_worksheet.write(submission_row, 1, submission.title)
    submissions_worksheet.write(submission_row, 2, submission.author)
    submissions_worksheet.write(submission_row, 3, submission.date_created)
    submissions_worksheet.write(submission_row, 4, submission.nsfw)
    submissions_worksheet.write(submission_row, 5, submission.post_type)
    submissions_worksheet.write(submission_row, 6, submission.upvote_ratio)
    submissions_worksheet.write(submission_row, 7, submission.total_awards)
    submissions_worksheet.write(submission_row, 8, submission.num_crossposts)
    submissions_worksheet.write(submission_row, 9, submission.text)
    submissions_worksheet.write(submission_row, 10, submission.video_duration)
    submissions_worksheet.write(submission_row, 11, submission.category)
    submissions_worksheet.write(submission_row, 12, submission.subreddit)

    submission_row += 1
    print(submission_row)


def add_comment(comment):
    global comment_row

    comments_worksheet.write(comment_row, 0, comment.id)
    comments_worksheet.write(comment_row, 1, comment.text)
    comments_worksheet.write(comment_row, 2, comment.author)
    comments_worksheet.write(comment_row, 3, comment.date_created)
    comments_worksheet.write(comment_row, 4, comment.parent_id)
    comments_worksheet.write(comment_row, 5, comment.submission_id)
    comments_worksheet.write(comment_row, 6, comment.upvote_ratio)
    comments_worksheet.write(comment_row, 7, comment.pinned)

    comment_row += 1


def add_crosspost(crosspost):
    global crosspost_row

    crossposts_worksheet.write(crosspost_row, 0, crosspost.crosspost_parent_id)
    crossposts_worksheet.write(crosspost_row, 1, crosspost.post_id)

    crosspost_row += 1


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
        add_subreddit(subreddit_info)
        for subm in submissions:
            add_submission(subm)
            for comm in subm.comments:
                add_comment(comm)

        for crossp in crossposts:
            add_crosspost(crossp)

        print(f"\t Saving information of subreddit: '{subreddit}'.")


def close_file():
    workbook.close()

# Example of collecting the information
# collect_subreddits(subreddits=["announcements"])
