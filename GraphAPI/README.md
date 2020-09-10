# Graph API Proof of Concept
This repo contains an implementation in Python which accesses the Azure Graph API.

## Application Registration
This implementation assumes an application registration has been configured in Azure. 
It should have the following properties:

- API Permissions: Microsoft Graph
    - Directory.Read.All
    - User.Read.All

## OAuth Authentication
This proof of concept uses the `client_credentials` flow (daemon service) and is
documented [here](https://docs.microsoft.com/en-us/graph/auth-v2-service). It is 
configured with the following properties:

- Endpoint: `https://login.microsoftonline.com/[tenant]/oauth2/v2.0/token`
    - grant_type: client_credentials
    - client_id: application id
    - client_secret: application secret
    - scope: `https://graph.microsoft.com/.default`
    
