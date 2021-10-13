import asyncio
import traceback
import unittest


def async_test(f):
    def wrapper(test_case: unittest.TestCase, *args, **kwargs):
        loop = asyncio.get_event_loop()
        task = loop.create_task(f(test_case, *args, **kwargs))
        try:
            loop.run_until_complete(task)
        except Exception:
            traceback.print_exc()
            raise

    return wrapper
