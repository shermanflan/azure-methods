import logging

from graph_api.exceptions import RetryableError, RetryExceededError
import graph_api.util.log

logger = logging.getLogger(__name__)


def _do_something(test_name, decision_tree):
    do_error, do_back_off = next(decision_tree)

    if do_error:
        logger.debug(f"{test_name}: Raising error with backoff = '{do_back_off}'.")
        raise RetryableError(f"Error in code block.", retry_after=3 if do_back_off else None)
    else:
        logger.debug(f"{test_name}: No error raised.")

    return 'Completed'


def _backoff(multiplier):
    power = 0

    while True:
        yield multiplier * (2 ** power)
        power += 1


def _actions():
    commands = [
        (True, True),  # do error, do backoff
        (True, True),
        (True, True),
        (True, False),
        (True, False),
        (True, False),
        (True, True),
        (True, True),
        (True, True),
        (True, False),
        (False, False),
        (True, False),
        (True, True),
        (True, True),
        (True, True),
        (True, False),
        (True, False),
        (True, False),
        (True, True),
        (True, True),
    ]
    for c in commands:
        yield c


def _retry_it(method, retries, multiplier):
    """
    Example showing dynamic retry strategy based on existence of
    "Retry-After".

    :param method:
    :param retries:
    :param multiplier:
    :return:
    """
    from time import sleep
    delay, delays, actions = 0, _backoff(multiplier), _actions()
    cycle = 0

    while cycle < retries:
        try:
            cycle += 1
            return method(decision_tree=actions)  # succeeded

        except RetryableError as e:
            logger.error(f"Retryable: {e}")

            if e.retry_after:
                logger.debug(f"Running for {cycle} with delay of {e.retry_after}.")
                sleep(e.retry_after)
                delay, delays = 0, _backoff(multiplier)  # reset
            else:
                delay += next(delays)
                logger.debug(f"Running for {cycle} with delay of {delay}.")
                sleep(delay)

    raise RetryExceededError("Retries exceeded.")


# def test_custom_retry():
#     from functools import partial
#
#     test_dynamic = partial(_do_something, test_name="test_dynamic_raise")
#     result = _retry_it(method=test_dynamic, retries=10, multiplier=1)
#
#     assert result == 'Completed'


def _retry(method):
    def redo(retries, multiplier, **kwargs):
        from time import sleep
        delay, delays = 0, _backoff(multiplier)
        cycle = 0

        while cycle < retries:
            try:
                cycle += 1
                return method(**kwargs)

            except RetryableError as e:
                logger.error(f"Retryable: {e}")

                if e.retry_after:
                    logger.debug(f"Running for {cycle} with delay of {e.retry_after}.")
                    sleep(e.retry_after)
                    delay, delays = 0, _backoff(multiplier)  # reset
                else:
                    delay += next(delays)
                    logger.debug(f"Running for {cycle} with delay of {delay}.")
                    sleep(delay)

        raise RetryExceededError("Retries exceeded.")

    return redo


def test_retry_decorate():
    test_dynamic = _retry(_do_something)
    result = test_dynamic(12, 1, test_name="test_redecorate",
                          decision_tree=_actions())

    assert result == 'Completed'
