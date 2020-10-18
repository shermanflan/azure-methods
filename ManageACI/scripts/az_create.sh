#!/bin/bash

declare RESOURCE_GROUP="ACIResourceGroup"
declare SUBSCRIPTION=""
declare LOCATION="eastus"
declare REGISTRY="rkoregistry"
declare CONTAINER_GROUP=""
declare IMAGE="box2lake:latest"
declare IDENTITY="ACIOperator"
declare YAML_CONFIG=box2lake-dev.yml

# az group create \
#   --location $LOCATION \
#   --name $RESOURCE_GROUP

# Create new ACR
# az acr create \
#   --resource-group $RESOURCE_GROUP \
#   --name $REGISTRY \
#   --admin-enabled true \
#   --sku Basic \
#   --location "$LOCATION" \
#   --subscription "$SUBSCRIPTION" \
#   --verbose

# Build and publish docker image to ACR
# cd ~/personal/devops/bshBoxAPI2ADLS
# az acr build --registry $REGISTRY --image $IMAGE .
# cd ~/personal/github/azure-methods/ManageACI/scripts

# Create service principal
#az ad sp create-for-rbac \
#  --name "http://$IDENTITY" \
#  --sdk-auth \
#  --role contributor \
#  --scopes /subscriptions/$SUBSCRIPTION/resourceGroups/$RESOURCE_GROUP \
#  > acioperator.auth.json

# Populate value required for subsequent command args
# ACR_REGISTRY_ID=$(az acr show --name $ACR_NAME --query id --output tsv)
# SERVICE_PRINCIPAL_ID=$(az ad sp show --id TestNewApp01 --query id --output tsv)

# Assign the desired role to the service principal. Modify the '--role' argument
# value as desired:
# acrpull:     pull only
# acrpush:     push and pull
# owner:       push, pull, and assign roles
# az role assignment create \
#   --assignee $SERVICE_PRINCIPAL_ID \
#   --role acrpull \
#   --scope $ACR_REGISTRY_ID

# Assign security role to a principal.
#az role assignment create \
#  --role Contributor \
#  --assignee $PRINCIPAL \
#  --subscription $SUBSCRIPTION \
#  --scope $APP_SCOPE

# az ad sp delete \
#   --id $IDENTITY

#az container create \
#  --resource-group $RESOURCE_GROUP \
#  --subscription $SUBSCRIPTION \
#  --file $YAML_CONFIG \
#  --verbose

# Start container instance
#az container start -n $CONTAINER_GROUP \
#  --resource-group $RESOURCE_GROUP \
#  --subscription $SUBSCRIPTION \
#  --verbose --debug

#az container delete \
#  --name $CONTAINER_GROUP \
#  --resource-group $RESOURCE_GROUP \
#  --subscription $SUBSCRIPTION

 az group delete \
   --name $RESOURCE_GROUP \
   --subscription $SUBSCRIPTION
