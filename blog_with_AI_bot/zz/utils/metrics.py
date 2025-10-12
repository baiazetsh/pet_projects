# zz/utils/metrics.py
from prometheus_client import Counter, Histogram

bot_replies = Counter('bot_replies_generated_total', 'Total bot replies generated')
summarize_duration = Histogram('summarize_post_duration_seconds', 'Duration of post summarization')

def track_bot_reply():
    bot_replies.inc()

def track_summarize_time(duration):
    summarize_duration.observe(duration)
