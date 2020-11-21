import asyncio
import logging
import json
import os

import azure.functions as func
import pyodbc

from utility import SQLConnection

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
            
            # Retrieve single JSON object
            result = cursor.execute(qry1, name+'%', int(limit))
            payload = result.fetchone() 
        
            return payload[0]

    except pyodbc.OperationalError as e:
        logging.error(f"{e.args[1]}")
        raise                        
    finally:
        pass


def main(req: func.HttpRequest,
         outputBlob: func.Out[func.InputStream]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    limit = req.params.get('limit', 500)

    if name and limit:
        logging.debug(f"TEST PARAM: {name}")
        logging.debug(f"TEST PARAM: {limit}")

        payload = get_meds(name, limit)

        response = func.HttpResponse(body=payload, 
                                     status_code=200,
                                     mimetype='application/json')
        
        logging.info('Saving payload as blob')
        outputBlob.set(json.dumps(json.loads(payload), indent=4))

        return response
    else:
        func.HttpResponse(json.dumps({'Bad Request': 'Parameters missing.'}), 
                          status_code=400,
                          mimetype='application/json')


    return func.HttpResponse(json.dumps({'Not Implemented': 'Undefined operation.'}), 
                             status_code=501,
                             mimetype='application/json')