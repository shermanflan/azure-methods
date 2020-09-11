import logging
from threading import Lock

import msal

from graph_api import (AAD_ENDPOINT, APP_ID, APP_SECRET)
import graph_api.logging

logger = logging.getLogger(__name__)


class OAuthFactory(object):
    """
    Implementation of a singleton for managing MSAL resource.

    TODO:
    - Is this the best way to implement the singleton/factory pattern in Python?

    Inspired by:
    - https://github.com/Azure-Samples/azure-sql-db-python-rest-api
    - https://github.com/Azure-Samples/ms-identity-python-daemon
    """
    __instance = None
    __connection = None
    __lock = Lock()

    def __new__(cls):
        if OAuthFactory.__instance is None:
            OAuthFactory.__instance = object.__new__(cls)
        return OAuthFactory.__instance

    def __get_connection(self):
        """
        Create a preferably long-lived app instance which maintains a
        token cache.

        TODO:
        Default cache is in memory only, but you can learn how to use
        SerializableTokenCache from
        https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache

        :return: the MSAL client
        """
        if not self.__connection:
            logger.info(f'Authenticating to Graph API...')

            self.__connection = msal.ConfidentialClientApplication(client_id=APP_ID,
                                                                   client_credential=APP_SECRET,
                                                                   authority=AAD_ENDPOINT)

        return self.__connection

    def __remove_connection(self):
        self.__connection = None

    def get_token(self, scopes):
        """
        This first looks up a token from the cache and generates if not found.
        Since the token is for the current app, NOT for an end user, note
        the account parameter as None.

        :param scopes:
        :return: the Bearer token as Dict
        """
        app = self.__get_connection()

        result = app.acquire_token_silent(scopes=scopes, account=None)

        if not result:
            logger.info("No token exists in cache. Generating a new one from AAD.")
            result = app.acquire_token_for_client(scopes=scopes)

        assert 'access_token' in result, "Bearer token could not be created."

        logger.info("Acquired bearer token from authority.")

        return result['access_token']
