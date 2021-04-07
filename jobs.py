from uwsgidecorators import *
import time

@timer(5)
def five_secs_elapsed():
    print('5 secs elapsed')