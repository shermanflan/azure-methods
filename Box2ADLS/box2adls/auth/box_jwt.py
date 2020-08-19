from boxsdk import JWTAuth, OAuth2, Client


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
