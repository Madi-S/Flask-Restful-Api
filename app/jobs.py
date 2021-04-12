from uwsgidecorators import *
import time

@timer(5)
def five_secs_elapsed(num):
    print('5 secs elapsed', num)


@filemon('secrets')
def notify_every_time_secret_files_changed_in_directory(name):   
    print('Boss, your secret directory files have been changed!', name)

@filemon('secrets/my_secret.txt')
def notify_every_time_secret_file_changed(name):   
    print('Boss, your secret file has been changed!', name)


@cron(-1, -1, -1, -1, -1)
def cron_every_minute(num):
    print('Cron is running every minute')

@cron(30, 17, -1, -1, -1)
def cron_at_five_thirty(num):
    print('it\'s 17:30pm. Time to go outside!')


# Similar to redis queue tasks, then this function can be called anywhere `some_job()`. However how can I get the job id?
@mulefunc
def some_job(*args, **kwargs):
    print('In some_job')
    for i in range(num):
        print(i)
        time.sleep(1)


@thread
def send_email_to(email='khovansky99@gmail.com', **kwargs):
    print('Sending email to', email, 'in a seperate thread')
    print('Done')

@thread
def sleep_thread():
    print('Gonna sleep for 2 seconds')
    time.sleep(2)
    print('Done with sleeping gotta work')

# Runs function in a seperate enclosed environment
@timer(2)
@lock
def locked_function(num):
    print('Concurrency sucks', num)