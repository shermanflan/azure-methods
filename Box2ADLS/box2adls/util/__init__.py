from datetime import timedelta


def get_last_friday(today):
    """
    Use date arithmetic to calculate the last Friday. Logic is based
    on calculating the offset between today and Friday. Then, this
    offset is added to get the "nearest" Friday. If this Friday is in
    the past, then it is returned. Otherwise, a week is subtracted
    from the future Friday and returned.

    See here for inspiration:
    https://stackoverflow.com/questions/12686991/how-to-get-last-friday

    :param today: current day
    :return: the last Friday (date)
    """
    # weekday(): Monday starts at 0 so Friday is 4.
    near_friday = today + timedelta(days=(4 - today.weekday()))

    if near_friday <= today:
        return near_friday
    else:
        return near_friday - timedelta(days=7)
