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

def search_highest_score_posts(reddit, subreddit_name='learnpython', 
                            keyword=None, limit=10, output_file='results.txt'):
    """
    Search for posts by keyword and return the highest scoring ones.
    Results are saved to a file.
    
    Args:
        reddit: PRAW Reddit instance
        subreddit_name: Name of subreddit to search in
        keyword: Search term (required)
        limit: Number of posts to return
        output_file: Name of file to save results to
    """
    if not keyword:
        print("Keyword is required for search")
        return
        
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        
        search_params = {
            'query': keyword,
            'sort': 'top',  
            'limit': limit
        }
        
        
        results = subreddit.search(**search_params)
        
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Search results for '{keyword}' in r/{subreddit_name}:\n")
            f.write("-" * 50 + "\n")
            
            
            for submission in results:
                
                f.write(f"\nTitle: {submission.title}\n")
                f.write(f"URL: {submission.url}\n")
                f.write(f"Score: {submission.score}\n")
                f.write(f"Comments: {submission.num_comments}\n")
                f.write("-" * 50 + "\n")
                
                
                # print(f"\n{'-'*20}")
                # print(f"Title: {submission.title}")
                # print(f"URL: {submission.url}")
                # print(f"Score: {submission.score}")
                # print(f"Comments: {submission.num_comments}")
                
        print(f"\nResults have been saved to {output_file}")
        
    except Exception as e:
        print(f"Failed to search posts: {e}")

if __name__ == "__main__":
    reddit = setup_reddit()
    if reddit:
        search_highest_score_posts(reddit, 
                                 subreddit_name='learnpython',
                                 keyword='python tutorial',
                                 limit=10,
                                 output_file='python_tutorials.txt')