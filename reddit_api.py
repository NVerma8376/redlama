import praw
from datetime import datetime

def setup_reddit():
    try:
        reddit = praw.Reddit(
            client_id='TBYCU3D0jqQLjqJKdUP4Jw',
            client_secret='p1oY9paKyEzvw4QMYxDsDDJmUpASpA',
            user_agent='reddit scraper by u/Naitik_POG'
        )
        return reddit
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        return None

def get_top_posts(reddit, subreddit_name='learnpython', limit=10):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        for submission in subreddit.top(limit=limit):
            print(f"\n{'-'*20}")
            print(f"Title: {submission.title}")
            print(f"URL: {submission.url}")
            print(f"Score: {submission.score}")
            print(f"Comments: {submission.num_comments}")
    except Exception as e:
        print(f"Failed to fetch posts: {e}")

# Usage
if __name__ == "__main__":
    reddit = setup_reddit()
    if reddit:
        get_top_posts(reddit)
