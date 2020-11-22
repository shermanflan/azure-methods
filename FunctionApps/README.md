# Serverless Functions Examples
This repo contains a demonstration of serverless functions on Azure.

## Features
- Web hook (HttpTrigger) with custom route and url prefix
- Event based publish/subscribe using Event Grid

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
Retry [settings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-error-pages?tabs=python#exponential-backoff-retry) 
can also be declared as follows.
```
{
  "version": "2.0",
  "retry": {
    "strategy": "exponentialBackoff",
    "maxRetryCount": 5,
    "minimumInterval": "00:00:30",
    "maximumInterval": "00:15:00"
  }
}
```
### [local.settings.json](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=csharp#local-settings-file)
Maintains local project settings such as connections strings. Only used 
when running locally.

- Set the `Values.AzureWebJobsStorage` key to a valid Azure Storage account 
connection string if testing Functions other than HttpTriggers.


### Add a new function
To add a new function to an existing VS Code project, follow these steps.

1. From the Azure Functions sidebar, select `Create Function`
2. Select from the available templates
3. Project settings should now be updated

## Deployment to Azure
Deployment to Azure can be automated via the Core Tools CLI or directly
in VS Code.

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
TBD

## Python Best Practices

- [General](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- Static [clients](https://docs.microsoft.com/en-us/azure/azure-functions/manage-connections#static-clients)
- [Asynchronous](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#async) 
patterns:
    - [aiohttp](https://pypi.org/project/aiohttp/)
    - [janus](https://pypi.org/project/janus/)
    - [aysncio](https://docs.python.org/3/library/asyncio-stream.html)
- [Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-best-practices)

## Function Types
### HttpTrigger
#### Trigger
An HttpTrigger responds to GET, POST, etc verbs. To setup a custom route,
modify the `function.json` with a `route` setting.
```
"bindings": [
    {
      "name": "req",
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "methods": [
        "get",
        "post"
      ],
      "route": "meds"
    }
...
```
In addition, if a route prefix is needed, then modify the `host.json` file
with an `http` extension as follows.
```
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[1.*, 2.0.0)"
  },
  "extensions": {
    "http": {
      "routePrefix": "rxapi/v1"
    }
  }
...
```
### [EventGrid](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-grid)
The [EventGridPublish](EventGridPublish/__init__.py) and 
[EventGridSubscribe](EventGridSubscribe/__init__.py) functions demonstrate 
event driven integration via Event Grid as the messaging technology.

#### Pre-requisites
In order to run the proof of concept, an Event Grid topic and subscription
need to exist. The topic is referenced as a binding in the function 
trigger's [function.json](EventGridPublish/function.json) configuration. 
The script [az_setup.sh](scripts/az_setup.sh) has been provided for the 
purpose of setting up a test topic and subscription. Be sure to set the 
environment variables according to your local Azure environment. The 
script assumes an Azure blob container exists to which it can send dead 
letters. 

The topic is configured with normal settings including public network 
access. The topic is protected via secret token so the endpoint is secure. 
For additional security, a private endpoint over a vnet can be configured
although this capability is still in preview as of this [writing](https://docs.microsoft.com/en-us/azure/event-grid/configure-private-endpoints). 
The subscription is configured with custom event types and [subject filtering](https://docs.microsoft.com/en-us/azure/event-grid/event-filtering#subject-filtering). 
Standard retry and TTL is also configured. The [advanced filtering](https://docs.microsoft.com/en-us/azure/event-grid/event-filtering#advanced-filtering) 
option supports inspection of the message payload, which may be useful in 
custom routing scenarios as shown in this [example](https://docs.microsoft.com/en-us/azure/event-grid/scripts/event-grid-cli-resource-group-filter#sample-script---preview-extension) 
but is not explored here.

#### Trigger
The [EventGridPublish](EventGridPublish/__init__.py) function is an HTTP
trigger setup to publish a message to the topic configured in the pre-
requisites. Its [function.json](EventGridPublish/function.json) settings
point to the topic id and key configured via an Event Grid output binding.

#### Input
The [EventGridSubscribe](EventGridSubscribe/__init__.py) function is setup
as a subscriber to the same topic. Its 
[function.json](EventGridPublish/function.json) includes an Event Grid 
trigger input binding. In addition, for testing purposes it uses a blob 
output binding as a destination where the message payload is written.

#### Testing
To trigger events, fire the [EventGridPublish](EventGridPublish/__init__.py) 
function from a web client of your choice. To publish to the topic directly 
for testing purposes, send a POST to the topic endpoint with a `aeg-sas-key`
header set to the topic access key. See this user guide for [details](https://docs.microsoft.com/en-us/azure/event-grid/post-to-custom-topic).
The request payload should be similar to the following [schema](https://docs.microsoft.com/en-us/azure/event-grid/event-schema). 
Notice the payload is enclosed in a JSON array.

```
[{
    "id": "test-id-3",
    "data": {
        "tag1": "frompostman",
        "tag2": "2"
    },
    "subject": "new-job-1",
    "eventType": "new-job-event-1",
    "eventTime": "2020-11-22T16:29:02.282524Z",
    "dataVersion": "1.0"
}]
```
A sample testing [script](scripts/az_sanity_test.sh) is included.

### Blob Storage
#### Trigger
TBD
#### Input
TBD
#### Output
A function can use a Blob container as an output binding. First, setup 
the `function.json` binding as follows.
```
{
  "name": "outputBlob",
  "type": "blob",
  "direction": "out",
  "path": "httptriggermeds/{rand-guid}",
  "connection": "AzureWebJobsStorage"
}
```
The blob can then be referenced as `func.InputStream` variable as shown in
the [example](HttpTriggerMeds/__init__.py).