from datetime import date, timedelta
from functools import partial
import logging
from os.path import split, join
from tempfile import TemporaryDirectory

from box2adls.exceptions import FolderMissingError
import box2adls.logging
from box2adls.util import get_last_friday
from box2adls.util.box import navigate, download_file
from box2adls.util.lake import upload_files
from box2adls.util.xlsx import transform_daily, transform_weekly


logger = logging.getLogger(__name__)


class EtlOperations:
    """
    Class encapsulating various ETL operations.
    """
    def __init__(self, box_client, lake_client, lake_root, target):
        """
        Standard constructor.

        :param box_client: box client with access to source folder
        :param lake_client: lake client
        :param lake_root: lake container
        :param target: lake target path
        """
        self.box_client = box_client
        self.lake_client = lake_client
        self.lake_root = lake_root
        self.lake_client = lake_client
        self.target = target

    def daily_pull(self, source, source_mask, source_rename, prev_label,
                   curr_label, next_label):
        """
        Routine which pulls daily files from Box.

        :param source: box source path
        :param source_mask: box file name filter
        :param source_rename: box output file name
        :param prev_label: New name of previous month tab
        :param curr_label: New name of current month tab
        :param next_label: New name of next month tab
        :return: None
        """
        today = date.today()
        prev_month = today.replace(day=1) - timedelta(days=1)

        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)

        partial_transform = partial(transform_daily,
                                    months=[prev_month.strftime("%B"),
                                            today.strftime("%B"),
                                            next_month.strftime("%B")],
                                    labels=[prev_label, curr_label, next_label])

        self.box_to_lake(source, source_mask, source_rename, partial_transform)

    def weekly_pull(self, source, source_mask, source_rename, tab_name,
                    tab_rename):
        """
        Routine which pulls weekly files from Box.

        :param source: box source path
        :param source_mask: box file name filter
        :param source_rename: box output file name
        :param tab_name: hidden tab name
        :param tab_rename: new tab name
        :return: None
        """
        today = date.today()
        last_friday = get_last_friday(today)
        source_week = join(source, last_friday.strftime("%B - %d"))

        partial_transform = partial(transform_weekly, tab_name, tab_rename)

        self.box_to_lake(source_week, source_mask, source_rename,
                         partial_transform)

    def box_to_lake(self, source, source_mask, source_rename, transform):
        """
        Routine which copies and transforms files from Box to the lake.

        :param source: box source path
        :param source_mask: box file name filter
        :param source_rename: box output file name
        :param transform: file function handler
        :return: None
        """
        box_root = self.box_client.folder('0').get()

        logger.info(f"Navigating Box path '{source}' on '{box_root.name}'")

        folders = source.split('/')[-1::-1]
        box_folder = navigate(box_root, folders)

        if not box_folder:
            raise FolderMissingError(f'Box folder "{split(source)[1]}" missing.')

        with TemporaryDirectory() as tmp_dir:

            logger.info(f'Downloading Box files from "{box_folder.name}"...')

            local_paths = download_file(box_folder=box_folder,
                                        file_mask=source_mask,
                                        file_name=source_rename,
                                        local_dir=tmp_dir)

            if local_paths:
                for i in local_paths:

                    logger.info(f'Applying transform to "{split(i)[1]}"...')

                    transform(source=i)

                logger.info(f'Uploading to lake "{self.target}"...')

                upload_files(self.lake_client, self.lake_root,
                             lake_dir=self.target, files=local_paths)
            else:
                logger.info(f'No Box files found in "{box_folder.name}"...')