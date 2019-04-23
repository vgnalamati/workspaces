from time import time
from functools import wraps


class execution_time(object):

    def __init__(self, **kwargs):
        self.func_name = kwargs.get('name', None)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start_time = time()
            func_return = func(*args, **kwargs)
            elapsed_time = time() - start_time
            if not self.func_name:
                self.func_name = func.__name__
            print("Total Execution time of {} is {:.2f} secs".format(self.func_name, elapsed_time))
        return wrapper
