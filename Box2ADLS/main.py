from os import environ
from os.path import join

from boxsdk import JWTAuth, OAuth2, Client
from boxsdk.object.collaboration import CollaborationRole

from box2adls.logging import root_logger as logger


def auth_jwt(box_config, user_id=None):
    """
    Authenticate via jwt private key file.

    :param box_config: private key file
    :param user_id: (optional) user to login as
    :return: Client
    """

    jwt_config = JWTAuth.from_settings_file(box_config)

    if user_id:
        jwt_config.authenticate_user(user=user_id)

    return Client(jwt_config)


def auth_app_token(app_token):
    """
    Authenticate via application token.

    :param app_token: application token
    :return: Client
    """
    auth = OAuth2(client_id=None, client_secret=None,
                  access_token=app_token)

    return Client(auth)


def has_collaboration(target_folder, target_user):
    """
    Check if the target folder is accessible by the given user.

    :param target_folder: the target folder
    :param target_user: the target user class
    :return: Boolean
    """
    collaborations = target_folder.get_collaborations()

    for c in collaborations:
        allowed_user = c.accessible_by

        if allowed_user == target_user:
            return True

    return False


if __name__ == '__main__':
    import logging
    logging.getLogger('boxsdk').setLevel(logging.ERROR)

    box_user_id = environ.get('BOX_USER_ID', '')
    box_folder_id = environ.get('BOX_FOLDER_ID', '')

    logger.info("Authenticating to Box API...")

    client_app = auth_jwt(box_config=join('config', 'box_config.json'))
    # Login as folder's app user to ensure collaboration.
    client_user = auth_jwt(box_config=join('config', 'box_config.json'),
                           user_id=box_user_id)

    service_user = client_app.user().get()
    logger.debug(f"Service: {service_user.name}")

    # To access data_source_01 under 'Ricardo', collaborations must be setup.
    root_folder = client_user.folder(folder_id=box_folder_id).get()

    logger.info(f"Verifying collaborations on '{root_folder.name}'")

    if not has_collaboration(target_folder=root_folder, target_user=service_user):
        logger.info(f"Creating collaboration for '{service_user.name}' on '{root_folder.name}'...")
        collaboration = root_folder.collaborate(service_user, CollaborationRole.VIEWER)

    root = client_app.folder('0').get()
    logger.info('Root: {0} "{1}" is named "{2}"'.format(root.type.capitalize(), root.id, root.name))

    items = root.get_items()
    for item in items:
        logger.info('Folder: {0} {1} is named "{2}"'.format(item.type.capitalize(), item.id, item.name))

    # file_id = '709093810685'
    # file_info = client.file(file_id).get()
    # logger.info('File "{0}" has a size of {1} bytes'.format(file_info.name, file_info.size))

