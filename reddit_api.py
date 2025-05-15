import praw
import json

def setup_reddit():
    try:
        reddit = praw.Reddit(
            client_id='TBYCU3D0jqQLjqJKdUP4Jw',
            client_secret='p1oY9paKyEzvw4QMYxDsDDJmUpASpA',
            user_agent='reddit comment scraper by u/Naitik_POG'
        )
        return reddit
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def scrape_current_affairs_comments(reddit, subreddit_name, keyword, limit, output_file):
    data = []

    try:
        subreddit = reddit.subreddit(subreddit_name)
        results = subreddit.search(query=keyword, sort='new', limit=limit)

        for post in results:
            post.comments.replace_more(limit=0)
            for comment in post.comments:
                data.append({
                    'title': post.title,
                    'comment': comment.body,
                    'score': comment.score,
                    'url': post.url
                })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        print(f"Collected {len(data)} comments on '{keyword}' into '{output_file}'")

    except Exception as e:
        print(f"Scraping failed: {e}")

if __name__ == "__main__":
    reddit = setup_reddit()
    if reddit:
        scrape_current_affairs_comments(
            reddit=reddit,
            subreddit_name='worldnews',
            keyword='iran conflict',
            limit=20,
            output_file='iran_conflict_comments.json'
        )
