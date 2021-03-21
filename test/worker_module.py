from func_module import count_words_at_url, say_hello
from redis import Redis
from rq import Queue
from datetime import timedelta, datetime

q = Queue(connection=Redis())

result = q.enqueue(count_words_at_url, 'http://nvie.com')
print(result)

# Schedule job to run at 9:15, October 10th
job = q.enqueue_at(datetime(2019, 10, 8, 9, 15), say_hello)

# Schedule job to be run in 10 seconds
job = q.enqueue_in(timedelta(seconds=10), say_hello)

job = q.enqueue_in(timedelta(seconds=10), count_words_at_url, ('http://nvie.com', ))