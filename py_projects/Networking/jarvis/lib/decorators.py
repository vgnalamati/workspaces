from time import time
from functools import wraps


def execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        func_return = func(*args, **kwargs)
        elapsed_time = time() - start_time
        print("Total Execution time of {} is {:.2f} secs".format(func, elapsed_time))
        return func_return
    return wrapper
