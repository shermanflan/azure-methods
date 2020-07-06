import logging
import json
import os

import azure.functions as func
import pyodbc


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    limit = req.params.get('limit', 500)
    cnxn_str = os.environ['SQL_CONNECTION']

    if name and limit:
        logging.debug(f"TEST PARAM: {name}")
        logging.debug(f"TEST PARAM: {limit}")

        try:

            # This calls cnxn.commit() when going out of scope.
            with pyodbc.connect(cnxn_str, autocommit=False) as cnxn:
                cursor = cnxn.cursor()

                qry1 = """
                    SELECT  TOP (?)
                            ID
                            , NAME
                            , DOSE
                    FROM    [dbo].[GlobalMedList] WITH (READUNCOMMITTED)
                    WHERE   NAME LIKE ?
                    ORDER BY ID
                    FOR JSON PATH;
                """    
                
                # Retrieve single JSON object
                result = cursor.execute(qry1, int(limit), name+'%')
                payload = result.fetchone()[0] 
            
                response = func.HttpResponse(body=payload, 
                                             status_code=200,
                                             mimetype='application/json')

            return response

        except pyodbc.OperationalError as e:
            logging.error(f"{e.args[1]}")
            raise                        
        finally:
            pass
    else:
        func.HttpResponse(json.dumps({'Bad Request': 'Parameters missing.'}), 
                          status_code=400,
                          mimetype='application/json')


    return func.HttpResponse(json.dumps({'Not Implemented': 'Undefined operation.'}), 
                             status_code=501,
                             mimetype='application/json')
