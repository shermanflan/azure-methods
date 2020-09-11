import logging

from graph_api import GRAPH_API_SCOPES
from graph_api.auth import OAuthFactory
from graph_api.api.graph import get_using_requests
import graph_api.logging

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    # TODO
    # Consider using subprocess/popen on bcp to sql or SqlAlchemy ORM
    #   https://docs.python.org/3/library/subprocess.html
    # Consider mounted volume to blob file system to persist delta link
    # Consider flat file output to json, csv, parquet
    # Consider writing success/failure to Teams
    # Incorporate Key Vault, Application Insights
    # Add asynchronous I/O?
    #   https://docs.python.org/3/library/asyncio.html

    get_using_requests(token=OAuthFactory().get_token(GRAPH_API_SCOPES))

    # TODO
    # Handle throttling: HTTP 429, Retry-After in response
    # Use $top with value < 20 to reduce throttling cost.
    #   https://docs.microsoft.com/en-us/azure/architecture/patterns/throttling
    # Handle server busy: HTTP 503/504, use exponential backoff
    # Handle bandwidth exceeded: HTTP 509, fatal
    # Use change tracking for delta updates to users after initial sync.
    #   https://docs.microsoft.com/en-us/graph/delta-query-users
    # Implement singleton/factory for connection resources
    #   https://github.com/Azure-Samples/azure-sql-db-python-rest-api/blob/master/app.py
    # Generate a unique GUID and send it on each Microsoft Graph REST request.
    #   This will help Microsoft investigate any errors more easily if you need
    #   to report an issue with Microsoft Graph.
    #   On every request to Microsoft Graph, generate a unique GUID, send it in
    #   the client-request-id HTTP request header, and also log it in your
    #   application's logs.
    #   Always log the request-id, timestamp and x-ms-ags-diagnostic from the HTTP
    #   response headers. These, together with the client-request-id, are required
    #   when reporting issues in Stack Overflow or to Microsoft Support.

    logger.info(f'Completed successfully...')
