from datetime import datetime


class Subreddit:
    """
    Model for a Subreddit.
    """
    name: str
    description: str
    date_created: datetime
    nsfw: bool
    subscribers: int

    def __init__(self, name: str, description: str, date_created, nsfw: bool, subscribers: int):
        self.name = name
        self.description = description
        self.date_created = datetime.utcfromtimestamp(date_created) if isinstance(date_created, float) else date_created
        self.nsfw = nsfw
        self.subscribers = subscribers

    def __str__(self):
        return f"Subreddit. " \
               f"\n\tname: '{self.name}'. " \
               f"\n\tdescription: '{self.description}'. " \
               f"\n\tdate_created: {self.date_created}. " \
               f"\n\tnsfw: {self.nsfw}. " \
               f"\n\tsubscribers: {self.subscribers}. "


class RedditComment:
    """
    Model for a RedditComment.
    """
    id: str
    author: str
    date_created: datetime
    parent_id: str
    submission_id: str
    upvote_ratio: float
    pinned: bool
    text: str
    replies: ["RedditComment"]

    def __init__(self, comment_id: str, text: str, author: str, date_created, parent_id: str, submission_id: str,
                 upvote_ratio: float, pinned: bool):
        self.id = comment_id
        self.author = author
        self.date_created = datetime.utcfromtimestamp(date_created) if isinstance(date_created, float) else date_created
        self.parent_id = parent_id
        self.submission_id = submission_id
        self.upvote_ratio = upvote_ratio
        self.pinned = pinned
        self.text = text
        self.replies = []

    def add_reply(self, reply: "RedditComment"):
        self.replies.append(reply)

    def __str__(self):
        return f"RedditComment. " \
               f"\n\tid: '{self.id}'. " \
               f"\n\tauthor: '{self.author}'. " \
               f"\n\tdate_created: {self.date_created}. " \
               f"\n\tparent_id: '{self.parent_id}'. " \
               f"\n\tsubmission_id: '{self.submission_id}'. " \
               f"\n\tupvote_ratio: {self.upvote_ratio}. " \
               f"\n\tpinned: {self.pinned}. " \
               f"\n\ttext: '{self.text}'. " \
               f"\n\treplies: {self.replies}"


class RedditSubmission:
    """
    Model for a RedditSubmission.
    """
    id: str
    title: str
    date_created: datetime
    author: str
    nsfw: bool
    comments: [RedditComment]
    post_type: str
    total_awards: int
    num_crossposts: int
    text: str
    subreddit: str
    upvote_ratio: float
    category: str
    video_duration: int

    def __init__(self, post_id: str, title: str, date_created, author: str, nsfw: bool, subreddit: str,
                 comments: [RedditComment], post_type: str, total_awards: int, num_crossposts: int, text: str,
                 upvote_ratio: float, category: str = None, video_duration: int = None):
        self.id = post_id
        self.title = title
        self.date_created = datetime.utcfromtimestamp(date_created) if isinstance(date_created, float) else date_created
        self.author = author
        self.nsfw = nsfw
        self.comments = comments
        self.post_type = post_type
        self.total_awards = total_awards
        self.num_crossposts = num_crossposts
        self.text = text
        self.upvote_ratio = upvote_ratio
        self.subreddit = subreddit
        self.category = category if category else ""
        self.video_duration = video_duration

    def __str__(self):
        return f"RedditSubmission. " \
               f"\n\tid: '{self.id}'. " \
               f"\n\ttitle: '{self.title}'. " \
               f"\n\tdate_created: {self.date_created}. " \
               f"\n\tauthor: '{self.author}'." \
               f"\n\tnsfw: {self.nsfw}. " \
               f"\n\tnum_comments: {len(self.comments)}. " \
               f"\n\tpost_type: {self.post_type}. " \
               f"\n\ttotal_awards: {self.total_awards}. " \
               f"\n\tnum_crossposts: {self.num_crossposts}." \
               f"\n\ttext: '{self.text}'." \
               f"\n\tupvote_ratio: {self.upvote_ratio}. " \
               f"\n\tcategory: '{self.category}'." \
               f"\n\tvideo_duration: {self.video_duration}.  "


class CrossPost:
    """
    Model for a CrossPost.
    """
    crosspost_parent_id: str
    post_id: str

    def __init__(self, parent_id: str, post_id: str):
        self.crosspost_parent_id = parent_id
        self.post_id = post_id

    def __str__(self):
        return f"CrossPost \n\t " \
               f"parent_id: {self.crosspost_parent_id} \n\t " \
               f"post_id: {self.post_id}"
