import asyncio
import logging
import json
import os

import azure.functions as func
import pyodbc

from utility.api.sql import SQLConnection

sql_client = SQLConnection('SQL_CONNECTION')


def get_meds(name, limit=500):
    """
    Get a list of meds.
    
    Enhancements:
    - Not sure async is working.
    :param cnxn_str: SQL connection
    :param name: name filter
    :param limit: limit filter
    :return: JSON string
    """

    try:

        with sql_client.get_conn().cursor() as cursor:

            qry1 = """
                SELECT  Id
                        , ProductBrandName
                        , PackageSize
                FROM    [MasterData].[ActiveProduct] WITH (READUNCOMMITTED)
                WHERE   ProductLabelName LIKE ?
                ORDER BY Id
                OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
                FOR JSON PATH;
            """    
            
            # Iterate through result
            result = cursor.execute(qry1, name+'%', int(limit))
            payload = ""
            for row in result:
                payload += row[0]

            return payload

    except pyodbc.OperationalError as e:
        logging.error(f"{e.args[1]}")
        raise                        
    finally:
        pass


def main(req: func.HttpRequest,
         outputBlob: func.Out[func.InputStream]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    limit = req.params.get('limit', 50)

    if name and limit:

        payload = get_meds(name, limit)

        response = func.HttpResponse(body=payload, 
                                     status_code=200,
                                     mimetype='application/json')
        
        logging.info(f'Saving payload as blob: {payload}')
        outputBlob.set(json.dumps(json.loads(payload), indent=4))

        return response
    else:
        func.HttpResponse(json.dumps({'Bad Request': 'Parameters missing.'}), 
                          status_code=400,
                          mimetype='application/json')


    return func.HttpResponse(json.dumps({'Not Implemented': 'Undefined operation.'}), 
                             status_code=501,
                             mimetype='application/json')