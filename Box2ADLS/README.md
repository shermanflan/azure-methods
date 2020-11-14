# Box2ADLS
Python-based ETL process to extract and transform documents from Box.com and land into an enterprise data lake.

* Python 3.8
* Key libraries used:
    * openpyxl: Excel manipulation
    * boxsdk: Box.com API
    * azure-storage-file-datalake: data lake API
* The process is Dockerized and configured to run on Azure Container Instances.

## Box.com API Access
API access to box.com is controlled via OAuth2. Using the box developer console,
an application registration has been created for this purpose, named `BOX_APP01_JWT`
so no further configuration is necessary. To re-generate the public/private key,
follow these steps:

1. Log into the box.com [developer console](https://rescare.app.box.com/developers/console)
using a personal login.
2. Click on `BOX_APP01_JWT`.
3. Go to Configuration.
4. Under `Add and Manage Public Keys`, remove the current key and click
`Genereate a Public/Private Keypair`.
5. This will download a new json config file.
6. This file should be placed under the `config` folder and named `my_config.json`.