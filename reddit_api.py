import praw
from nltk.tokenize import sent_tokenize
from collections import Counter
import re

def setup_reddit():
    try:
        reddit = praw.Reddit(
            client_id='TBYCU3D0jqQLjqJKdUP4Jw',
            client_secret='p1oY9paKyEzvw4QMYxDsDDJmUpASpA',
            user_agent='reddit scraper by u/Naitik_POG',
            username='Naitik_POG',
            password='NVermaGamingMineCraft',
            check_for_async=False
        )
        reddit.read_only = True
        reddit.user.me()  # Check credentials
        return reddit
    except Exception as e:
        print(f"❌ Failed to authenticate with Reddit: {e}")
        return None

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()

def extract_comments(submission):
    submission.comments.replace_more(limit=0)
    return [clean_text(comment.body) for comment in submission.comments.list() if comment.body]

def summarize_text(text, max_sentences=4, question=""):
    question_keywords = set(re.findall(r'\w+', question.lower()))
    sentences = sent_tokenize(text)
    word_freq = Counter(re.findall(r'\w+', text.lower()))

    sentence_scores = {}
    for sent in sentences:
        words = re.findall(r'\w+', sent.lower())
        base_score = sum(word_freq[word] for word in words)
        relevance_bonus = sum(3 for word in words if word in question_keywords)
        sentence_scores[sent] = base_score + relevance_bonus

    ranked = sorted(sentence_scores, key=lambda sent: sentence_scores[sent], reverse=True)
    summary_sentences = ranked[:max_sentences]

    # Join sentences with space to make 3-4 lines paragraph
    summary = ' '.join(summary_sentences)
    return summary

def search_and_summarize(reddit, keyword, subreddit='all', post_limit=10):
    print(f"🔎 Searching Reddit for: {keyword}")
    subreddit = reddit.subreddit(subreddit)
    results = subreddit.search(keyword, sort='top', limit=post_limit)

    all_comments = []
    for post in results:
        print(f"📥 Fetching comments from: {post.title}")
        all_comments.extend(extract_comments(post))

    if not all_comments:
        print("⚠️ No comments found.")
        return

    combined = ' '.join(all_comments)
    summary = summarize_text(combined, question=keyword)

    with open("all_comments.txt", "w", encoding="utf-8") as f:
        f.write(combined)

    print("\n📌 Summarized Answer:\n")
    print(summary)

if __name__ == "__main__":
    reddit = setup_reddit()
    if reddit:
        question = input("Ask your question: ").strip()
        if question:
            search_and_summarize(reddit, question)
        else:
            print("⚠️ You must enter a question.")
