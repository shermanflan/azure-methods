# Serverless Functions Examples
This repo contains a demonstration of serverless functions on Azure.

## Features

## Setup
Using Azure Functions with Python has the following pre-requisites.

1. VS Code with the Python and Azure Functions extensions installed
2. Azure Functions Core Tools [version 3.x+](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash)
    - To install on Ubuntu follow this [guidance](https://www.npmjs.com/package/azure-functions-core-tools)

## Local Development
Using the Functions Core Tools CLI, VS code can be used to run the Function
App locally in debug mode. To prepare your environment for local testing
the following steps are necessary.

1. Create a virtual python environment with any additional libraries
your functions require
    - Make sure the environment folder is named `.venv` or the Core Tools
    CLI may not see it
    - In addition, as of this writing python 3.8+ does not play well 
    with the Core Tools CLI, so stick to 3.7-
2. Click F5 to debug

## Deployment to Azure
Deployment to Azure can be automated via the Core Tools CLI or directly
in VS Code. Both options will be explored here.

### Deployment via VS Code
This is a convenient option for deploying the Azure Functions to Azure.

1. Click the Deploy icon from the Azure Functions side bar
2. Walk through the wizard and deploy to the target region
    - Note, by default this creates a new resource group and the 
    following artifacts: storage account, Function App, and Application
    Insights, and a Linux App Service plan
3. Under Settings/Configuration, add any environment variables your
functions require
4. The deployment is now complete

### Deployment via Func Tools CLI
