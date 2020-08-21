from os.path import join

from boxsdk.object.collaboration import CollaborationRole

from box2adls.logging import root_logger as logger


def check_or_create_collab(box_user_client, box_service_client, box_folder_id):
    """
    Verify the target folder is accessible by the given user.
    Create collaboration otherwise.

    :param box_user_client: the user client with access to folder
    :param box_service_client: the service client
    :param box_folder_id: the target folder root
    :return: The collaboration object
    """
    service_user = box_service_client.user().get()
    box_folder = box_user_client.folder(folder_id=box_folder_id).get()

    logger.info(f"Verifying Box collaboration on '{box_folder.name}' " +
                f"for {service_user.name}")

    if not has_collab(box_folder, service_user):
        logger.info(f"Adding Box collab '{service_user.name}' on '{service_user.name}'...")

        return box_folder.collaborate(service_user, CollaborationRole.VIEWER)


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


def download_file(box_folder, file_mask, file_name, local_dir):
    """
    Download filtered files to target directory.

    :param box_folder: the source folder in Box
    :param file_mask: file name filter
    :param file_name: output file name
    :param local_dir: the local folder
    :return: list of downloaded file paths
    """
    items = box_folder.get_items()
    downloads = []

    for i in items:

        logger.debug(f'Comparing "{i.name}" and "{file_mask}"')

        if i.type == 'file' and i.name == file_mask:
            if file_name:
                download_path = join(local_dir, file_name)
            else:
                download_path = join(local_dir, i.name)

            with open(download_path, 'wb') as f:
                i.download_to(f)
                downloads.append(download_path)

            logger.info(f'Downloaded Box file: "{download_path}"')

            break

    return downloads
