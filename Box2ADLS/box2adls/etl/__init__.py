from datetime import date, timedelta
from functools import partial
from os.path import split, join
from tempfile import TemporaryDirectory

from box2adls.logging import root_logger as logger
from box2adls.util import get_last_friday
from box2adls.util.box import navigate, download_file
from box2adls.util.lake import upload_files
from box2adls.util.xlsx import transform_daily, transform_weekly


def daily_pull(box_client, source, source_mask, source_rename,
               prev_label, curr_label, next_label,
               lake_client, lake_root, target):
    """
    Routine which pulls daily files from Box.

    :param box_client: box client with access to source folder
    :param source: box source path
    :param source_mask: box file name filter
    :param source_rename: box output file name
    :param prev_label: New name of previous month tab
    :param curr_label: New name of current month tab
    :param next_label: New name of next month tab
    :param lake_client: lake client
    :param lake_root: lake container
    :param target: lake target path
    :return: None
    """
    today = date.today()
    curr_month = date.strftime(today, '%B')
    prev_month = today.replace(day=1) - timedelta(days=1)
    prev_month = prev_month.strftime("%B")

    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    next_month = next_month.strftime("%B")

    logger.debug(f'prev: {prev_month}, curr: {curr_month}, next: {next_month}')

    partial_transform = partial(transform_daily,
                                prev_month=prev_month, prev_label=prev_label,
                                curr_month=curr_month, curr_label=curr_label,
                                next_month=next_month, next_label=next_label)

    box_to_lake(box_client, source, source_mask, source_rename,
                lake_client, lake_root, target, partial_transform)


def weekly_pull(box_client, source, source_mask, source_rename,
                tab_name, tab_rename, lake_client, lake_root,
                target):
    """
    Routine which pulls weekly files from Box.

    :param box_client: box client with access to source folder
    :param source: box source path
    :param source_mask: box file name filter
    :param source_rename: box output file name
    :param tab_name: hidden tab name
    :param tab_rename: new tab name
    :param lake_client: lake client
    :param lake_root: lake container
    :param target: lake target path
    :return: None
    """
    today = date.today()
    last_friday = get_last_friday(today)
    week_mask1 = date.strftime(last_friday, '%B - %d')
    source_week = join(source, week_mask1)
    logger.debug(f'Last Friday: {last_friday}')
    logger.debug(f'Last Friday: {week_mask1}')
    logger.debug(f'Full path: {source_week}')

    partial_transform = partial(transform_weekly, tab_name=tab_name,
                                tab_rename=tab_rename)

    box_to_lake(box_client, source_week, source_mask, source_rename,
                lake_client, lake_root, target, partial_transform)


def box_to_lake(box_client, source, source_mask, source_rename,
                lake_client, lake_root, target, transform):
    """
    Routine which copies folders from Box to ADLS.

    :param box_client: box client with access to source folder
    :param source: box source path
    :param source_mask: box file name filter
    :param source_rename: box output file name
    :param lake_client: lake client
    :param lake_root: lake container
    :param target: lake target path
    :param transform: file function handler
    :return: None
    """
    box_root = box_client.folder('0').get()

    logger.info(f"Navigating Box path '{source}' on '{box_root.name}'")

    folders = source.split('/')[-1::-1]
    box_folder = navigate(box_root, folders)

    if not box_folder:
        raise Exception(f'Box folder "{split(source)[1]}" not found.')

    with TemporaryDirectory() as tmp_dir:

        logger.info(f'Downloading Box files from "{box_folder.name}"...')

        local_paths = download_file(box_folder=box_folder, file_mask=source_mask,
                                    file_name=source_rename, local_dir=tmp_dir)

        if local_paths:
            for i in local_paths:
                logger.info(f'Applying transformation to "{split(i)[1]}"...')
                transform(source=i)

            logger.info(f'Uploading to lake "{target}"...')

            upload_files(lake_client, lake_root, lake_dir=target,
                         files=local_paths)
        else:
            logger.info(f'No Box files found in "{box_folder.name}"...')