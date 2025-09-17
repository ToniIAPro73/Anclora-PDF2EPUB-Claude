#!/usr/bin/env python3
import redis

try:
    r = redis.Redis(
        host='localhost',
        port=6379,
        password='XNdpx7I-taa6vZDF3ttieYd1gxs0oE9e9xHt4utbkCQ',
        db=0
    )
    print("Redis connected:", r.ping())
    print("Celery tasks in queue:", len(r.keys('celery-task-meta-*')))

    # Check if there are any Celery workers registered
    workers = r.smembers('_kombu.binding.celery')
    print("Active workers:", len(workers))

except Exception as e:
    print("Redis connection failed:", e)