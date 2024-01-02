import functools
import logging
import time


def cache_by_time(seconds):
    def decorator(func):
        cached_results = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in cached_results:
                result, timestamp = cached_results[key]
                if time.time() - timestamp < seconds:
                    logging.debug(f"Cache hit for {key}")
                    return result

            logging.debug(f"Cache miss for {key}")
            result = func(*args, **kwargs)
            cached_results[key] = (result, time.time())
            return result

        return wrapper

    return decorator
