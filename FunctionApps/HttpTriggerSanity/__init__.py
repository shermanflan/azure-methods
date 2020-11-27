import logging
import io
import os
from tempfile import TemporaryDirectory
import uuid
from zipfile import ZipFile

import azure.functions as func

from utility.api.lake import DataLakeHook
from utility.api.soap import OracleFusionHook

lake_client = DataLakeHook(
    lake_url=os.environ['LAKE_URL'], 
    lake_key=os.environ['LAKE_KEY'])
erp_client = OracleFusionHook(
    user=os.environ['FUSION_USER'], 
    password=os.environ['FUSION_USER_PWD'], 
    soap_uri=os.environ['SOAP_URI'], 
    erp_uri=os.environ['ERP_URI'])

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    file_name_prefix = req.params.get('file_name_prefix', 'MANIFEST_DATA_41')
    lake_container = req.params.get('lake_container', 'event-grid-subscribe')
    lake_path = req.params.get('lake_path', 'output')

    search_query = f"""
    dOriginalName <starts> `{file_name_prefix}`
    <AND> dSecurityGroup <starts> `OBIAImport`
    """.strip()

    logging.info(f"Searching files for '{file_name_prefix}'")

    try:
        results_df = erp_client.get_search_results(search_query)
    except Exception as e:
        logging.info(e.msg)
        logging.exception(e)
        raise

    if results_df.shape[0] > 0:
        logging.info(f"Found {results_df.shape[0]} documents")
    else:
        raise Exception(f"No documents found")

    for r in results_df.itertuples(index=False):
        logging.info(f"Downloading {r.dOriginalName} to {lake_path}")

        docs_df, content = erp_client.get_content(r.dID)

        for attach in content:

            logging.info(f"Uploading to lake")

            content_type = docs_df.loc[
                docs_df.dOriginalName == attach['href'],
                'dFormat'].iloc[0]

            if content_type == 'application/zip':
                with ZipFile(io.BytesIO(attach['Contents'])) as z:  # ?
                    for member in z.infolist():
                        file_name = f"{uuid.uuid4()}-{member.filename}"
                        data = z.open(name=member.filename)

                        lake_client.upload_data(lake_container=lake_container,
                                                lake_dir=lake_path,
                                                file_name=file_name,
                                                data=data.read())
            else:
                file_name = f"{uuid.uuid4()}-{attach['href']}"
                
                lake_client.upload_data(lake_container=lake_container,
                                        lake_dir=lake_path,
                                        file_name=file_name,
                                        data=attach['Contents'])

        logging.info(f"Downloaded {docs_df.shape[0]} documents")

    logging.info(f'Python EventGrid trigger processed an event')

    return func.HttpResponse(body='Python EventGrid trigger processed an event',
                             status_code=200,
                             mimetype='application/json')
