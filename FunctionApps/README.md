# Serverless Functions Examples
This repo contains a demonstration of serverless functions on Azure.

## Features

## Pre-requisites
Using Azure Functions with Python has the following pre-requisites.

1. VS Code with the Python and Azure Functions [extensions installed](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#install-the-azure-functions-extension)
2. Azure Functions Core Tools [version 3.x+](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash)
    - To [install](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash#v2) 
    on Ubuntu follow this 
    [guidance](https://www.npmjs.com/package/azure-functions-core-tools)

## Initial Project Setup
### VS Code
To setup a local environment for Azure Functions development in VS Code,
follow these steps.

1. Create a project folder
2. From the Azure Functions sidebar, select `Create Function`
3. Go through the wizard and select the language, virtual environment,
and function class
    - Make sure the virtual environment folder is named `.venv` or the 
    Core Tools CLI may not see it
    - As of this writing python 3.8+ does not play well with the Core 
    Tools CLI, so stick to 3.7-
4. The initial template is loaded to your project folder

### Core Tools
[TBD](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash#v2)

## Local Development
 
### VS Code
VS code can be used to run the Function App locally in debug mode. To 
prepare your environment for local testing the following steps are 
necessary.

1. Add any project settings to the `local.settings.json` file
2. Add any library dependencies to `requirements.txt`
3. Click F5 to debug

### Core Tools
Using the Functions Core Tools CLI, the function app can be tested
locally as follows.

1. Activate the virtual environment for your project
2. From the project root folder, run `func host start`

## Project Settings
Settings and methodology specific to function projects are discussed
below.

### [host.json](https://docs.microsoft.com/en-us/azure/azure-functions/functions-host-json)
Modifies the functions host locally and when deployed to Azure. One use
of this configuration file is to add custom route prefixes to the 
function app as shown below.

```
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "rxapi/v1"
    }
  }
}
```
### [local.settings.json](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#local-settings-file)
Maintains local project settings such as connections strings. Only used 
when running locally.

- Set the `Values.AzureWebJobsStorage` key to a valid Azure Storage account 
connection string if testing Functions other than HttpTriggers.

## Deployment to Azure
Deployment to Azure can be automated via the Core Tools CLI or directly
in VS Code. Both options will be explored here.

### Deployment via VS Code
This is a convenient option for deploying the Azure Functions to Azure.

1. Click the Deploy icon from the Azure Functions side bar
    - Select `Create new Function App... Advanced`
2. Walk through the wizard and deploy to the target region
    - Note, by default this creates a Linux App Service plan in the same
    resource group selected for the Function App
3. Under Settings/Configuration, add any environment variables your
functions require
4. The deployment is now complete

### Deployment via Func Tools CLI

## Python Best Practices
[TBD](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)

- Static [clients](https://docs.microsoft.com/en-us/azure/azure-functions/manage-connections#static-clients)