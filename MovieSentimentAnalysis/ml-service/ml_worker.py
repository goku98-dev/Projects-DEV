import redis
from rq import Worker, Queue
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import process_sentiment 

if __name__ == '__main__':
    print("Starting ML Worker...")
    
    redis_conn = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    worker = Worker(['sentiment_analysis'], connection=redis_conn)
    
    print("Worker started, waiting for jobs...")
    worker.work()