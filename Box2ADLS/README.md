# Box2ADLS
Python-based ETL process to extract and transform documents from Box.com and land into an enterprise data lake.

* Python 3.8
* Key libraries used:
    * openpyxl: Excel manipulation
    * boxsdk: Box.com API
    * azure-storage-file-datalake: data lake API
* The process is Dockerized and configured to run on Azure Container Instances.