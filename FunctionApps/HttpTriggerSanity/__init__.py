import logging
import os
from tempfile import TemporaryDirectory

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

    file_name = req.params.get('file_name', 'MANIFEST_DATA_41')
    lake_container = req.params.get('lake_container', 'event-grid-subscribe')
    lake_path = req.params.get('lake_path', 'output')

    search_query = f"""
    dOriginalName <starts> `{file_name}`
    <AND> dSecurityGroup <starts> `OBIAImport`
    """.strip()

    logging.info(f"Searching files for '{search_query}'")

    results_df = erp_client.get_search_results(search_query)

    if results_df.shape[0] > 0:
        logging.info(f"Found {results_df.shape[0]} documents")
    else:
        raise Exception(f"No documents found")

    with TemporaryDirectory() as tmp_folder:
    # tmp_folder = './jupyter/data'

        for r in results_df.itertuples(index=False):
            logging.info(f"Downloading {r.dOriginalName} to {tmp_folder}")

            docs_df, content = erp_client.get_content(r.dID)

            for attach in content:
                tmp_path = os.path.join(tmp_folder, attach['href'])

                content_type = docs_df.loc[
                    docs_df.dOriginalName == attach['href'],
                    'dFormat'].iloc[0]

                logging.info(f"Uploading to lake")

                if content_type == 'application/zip':
                    with open(tmp_path, 'wb') as f:
                        f.write(attach['Contents'])

                    with ZipFile(tmp_path) as z:
                        for member in z.infolist():
                            data = z.open(name=member.filename)
                            lake_client.upload_data(lake_container=lake_container,
                                                    lake_dir=lake_path,
                                                    file_name=member.filename,
                                                    data=data)
                else:
                    lake_client.upload_data(lake_container=lake_container,
                                            lake_dir=lake_path,
                                            file_name=attach['href'],
                                            data=attach['Contents'])

            logging.info(f"Downloaded {docs_df.shape[0]} documents")


    return func.HttpResponse(f"This HTTP triggered function executed successfully.")
