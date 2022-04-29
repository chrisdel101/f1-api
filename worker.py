from rq import Worker, Queue, Connection
from dotenv import load_dotenv, find_dotenv
import os
import redis

if os.environ.get('FLASK_ENV'):
    if os.environ['FLASK_ENV'] == 'development':
        load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))
else:
    load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))


listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
