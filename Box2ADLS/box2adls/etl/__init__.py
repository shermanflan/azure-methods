from os.path import split
from tempfile import TemporaryDirectory

from box2adls.logging import root_logger as logger
from box2adls.util.box import navigate, download_file
from box2adls.util.lake import upload_files


def box_to_lake(box_client, source, source_mask, source_rename,
                lake_client, lake_root, target):
    """
    Routine which copies folders from Box to ADLS.

    :param box_client: box client with access to source folder
    :param source: box source path
    :param source_mask: box file name filter
    :param source_rename: box output file name
    :param lake_client: lake client
    :param lake_root: lake container
    :param target: lake target path
    :return: None
    """
    box_root = box_client.folder('0').get()

    logger.info(f"Navigating Box path '{source}' on '{box_root.name}'")

    folders = source.split('/')[-1::-1]
    daily = navigate(box_root, folders)

    if not daily:
        raise Exception(f'Daily folder "{split(source)[1]}" not found.')

    with TemporaryDirectory() as tmp_dir:

        logger.info(f'Downloading Box files from "{daily.name}"...')

        local_paths = download_file(box_folder=daily, file_mask=source_mask,
                                    file_name=source_rename, local_dir=tmp_dir)

        if local_paths:
            logger.info(f'Uploading to lake "{target}"...')

            upload_files(lake_client, lake_root, lake_dir=target,
                         files=local_paths)
        else:
            logger.info(f'No Box files found in "{daily.name}"...')