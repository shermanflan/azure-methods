import asyncio
import logging
import json
import os

import azure.functions as func
import pyodbc


async def get_meds(cnxn_str, name, limit=500):
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

        with pyodbc.connect(cnxn_str, autocommit=True) as cnxn:
            cursor = cnxn.cursor()

            qry1 = """
                SELECT  ID
                        , NAME
                        , DOSE
                FROM    [dbo].[GlobalMedList] WITH (READUNCOMMITTED)
                WHERE   NAME LIKE ?
                ORDER BY ID
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


async def main(req: func.HttpRequest): 
    """
    Inspired by:
    https://github.com/Azure-Samples/azure-sql-db-python-rest-api/blob/master/app.py
    https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#async

    :param req: the HttpRequest
    :return: HttpResponse
    """

    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    limit = req.params.get('limit', 500)
    cnxn_str = os.environ['SQL_CONNECTION']

    if name and limit:
        logging.debug(f"TEST PARAM: {name}")
        logging.debug(f"TEST PARAM: {limit}")

        payload = await get_meds(cnxn_str, name, limit)

        response = func.HttpResponse(body=payload, 
                                        status_code=200,
                                        mimetype='application/json')

        return response
    else:
        func.HttpResponse(json.dumps({'Bad Request': 'Parameters missing.'}), 
                          status_code=400,
                          mimetype='application/json')


    return func.HttpResponse(json.dumps({'Not Implemented': 'Undefined operation.'}), 
                             status_code=501,
                             mimetype='application/json')
