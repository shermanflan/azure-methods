from os.path import join

from boxsdk.object.collaboration import CollaborationRole

from box2adls.logging import root_logger as logger


def check_or_create_collab(box_folder, box_user):
    """
    Verify the target folder is accessible by the given user.
    Create collaboration otherwise.

    :param box_folder: the target folder
    :param box_user: the target user class
    :return: The collaboration object
    """

    if not has_collab(box_folder, box_user):
        logger.info(f"Adding Box collab '{box_user.name}' on '{box_user.name}'...")

        return box_folder.collaborate(box_user, CollaborationRole.VIEWER)


def has_collab(box_folder, box_user):
    """
    Check if the target folder is accessible by the given user.

    :param box_folder: the target folder
    :param box_user: the target user class
    :return: Boolean
    """
    collaborations = box_folder.get_collaborations()

    for c in collaborations:
        allowed_user = c.accessible_by

        if allowed_user == box_user:
            return True

    return False


def navigate(box_folder, folders):
    """
    Navigates through a path list and returns the last folder in the path.

    :param box_folder: the staring box folder
    :param folders: the folder path to navigate
    :return: Last folder in given path
    """
    if not folders:
        return box_folder

    current_folder = folders.pop()

    items = box_folder.get_items()

    for i in items:

        if i.type == 'folder' and i.name == current_folder:
            logger.debug(f'Box Folder: {i.type} {i.id} is named "{i.name}"')
            return navigate(i, folders)

    return None


def download_files(box_folder, local_dir):
    """
    Download all files to target directory.

    :param box_folder: the source folder in Box
    :param local_dir: the local folder
    :return: list of downloaded file paths
    """
    items = box_folder.get_items()
    downloads = []

    for i in items:

        if i.type == 'file':
            download_path = join(local_dir, i.name)

            with open(download_path, 'wb') as f:
                i.download_to(f)
                downloads.append(download_path)

            logger.info(f'Downloaded Box file: "{download_path}"')

    return downloads
