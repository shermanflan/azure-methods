from datetime import datetime, timedelta
import logging

from tenacity import (Retrying, retry, stop_after_attempt, RetryError,
                      TryAgain, wait_fixed, wait_exponential,
                      retry_if_result, before_log, before_sleep_log)

from graph_api.exceptions import RetryableError
import graph_api.util.log

logger = logging.getLogger(__name__)

"""
Test routines for validating retry algorithms.
"""


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def _stop_after_x_attempts(times):
    logger.info(f"Attempts left: {times['times']}")
    times['times'] -= 1
    raise RetryableError(f"Simulated error...{times['times']}")


def test_retry_after():
    times_x = {'times': 3}
    try:
        _stop_after_x_attempts(times_x)
    except RetryError as e:
        pass

    assert times_x['times'] == 0


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=5))
def _exponential_backoff(times):
    ts = datetime.now()
    logger.info(f"Attempts left: {times['times']}, {ts - times['ts']}")
    times['delta'] = ts - times['ts']
    times['ts'] = ts
    times['times'] -= 1

    raise RetryableError(f"Simulated error...{times['times']}")


def test_retry_backoff():
    times_x = {'times': 5, 'ts': datetime.now()}
    try:
        # 0, 5*2^0 = 5, 5*2^1=10, 5*2^2 = 20, 5*2^3 = 40
        _exponential_backoff(times_x)
    except RetryError as e:
        pass

    assert times_x['times'] == 0 \
           and times_x['delta'] >= timedelta(seconds=40)


def _is_backoff(value):
    """

    :param value: Set to result of decorated function
    :return:
    """
    return value and isinstance(value, int)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1),
       retry=retry_if_result(_is_backoff),
       before=before_log(logger, logging.DEBUG))
def _might_return_backoff():
    return 30


def test_conditional_retry():
    """
    Example of retrying based on return result.
    :return:
    """
    try:
        _might_return_backoff()
    except RetryError as e:
        pass

    assert True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1),
       before_sleep=before_sleep_log(logger, logging.DEBUG))
def _manual_retry():
    raise TryAgain()


def test_try_again():
    """
    Example of retrying imperatively.
    :return:
    """
    try:
        _manual_retry()
    except RetryError as e:
        pass

    assert True


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1),
       before=before_log(logger, logging.DEBUG))
def _raise_my_exception():
    raise RetryableError(f"Simulated error with backoff.", retry_after=10)


def test_dynamic_retry():
    """
    Example of changing retry args at run-time.
    :return:
    """
    try:
        _raise_my_exception.retry_with(wait=wait_fixed(10))()
    except RetryError as e:
        pass

    assert True


def _flaky_function(message):
    raise RetryableError(f"Simulated error '{message}'.", retry_after=10)


def test_imperative():
    """
    Example demonstrating using Retrying directly.

    :return:
    """
    max_attempts = 3
    back_off = 5
    redo = Retrying(stop=stop_after_attempt(max_attempts),
                    reraise=True, wait=wait_fixed(back_off),
                    before=before_log(logger, logging.DEBUG))

    try:
        redo(_flaky_function, 'I really do try')
    except RetryableError as e:
        logger.error(f"Retryable: {e}, {e.retry_after}")


def test_code_block():
    """
    Example demonstrating using Retrying in a code block.

    :return:
    """
    try:
        tries = 3
        back_off = 2

        for attempt in Retrying(stop=stop_after_attempt(tries),
                                wait=wait_fixed(back_off), reraise=True):
            with attempt:
                logger.info(f"Attempts left in block: {tries}")
                tries -= 1
                raise RetryableError(f"Simulated error in code block.", retry_after=10)

    except RetryableError as e:
        logger.error(f"Retryable: {e}")
