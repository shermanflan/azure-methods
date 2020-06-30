#!/bin/bash -eux

declare CONTAINER="cds-python"
declare RESOURCE_GROUP=""
declare SUBSCRIPTION=""
declare REGISTRY=""
declare LOCATION="East US"
declare IMAGE="cdspython:1.0"
declare ENV_TENANT=""
declare ENV_CLIENT=""
declare ENV_RESOURCE=""
declare ENV_SECRET=""
declare REGISTRY_URL=""
declare REGISTRY_USER=""
declare REGISTRY_PWD=""

# Create new ACR
#az acr create --resource-group $RESOURCE_GROUP \
#  --name $REGISTRY \
#  --admin-enabled true --sku Basic \
#  -l $LOCATION \
#  --subscription $SUBSCRIPTION

# Enable admin account for invocation from ACI
#az acr update -n $REGISTRY --admin-enabled true

# Build and publish docker image to ACR
#az acr build --registry $REGISTRY --image $IMAGE .

# Alternative publish using native Docker
#docker login $REGISTRY_URL
#docker tag python-cds $REGISTRY_URL/$IMAGE
#docker push $REGISTRY_URL/$IMAGE

# TODO: Can be defined using YAML file.
# Create new container group
#az container create \
#  --resource-group $RESOURCE_GROUP \
#  --name $CONTAINER \
#  --image $REGISTRY_URL/$IMAGE \
#  -l $LOCATION \
#  --os-type Linux --cpu 1 --memory 1.5 \
#  --restart-policy Never \
#  --environment-variables \
#    AAD_TENANT=$ENV_TENANT \
#    AAD_CLIENT=$ENV_CLIENT \
#    AAD_RESOURCE=$ENV_RESOURCE \
#  --secure-environment-variables \
#    AAD_SECRET=$ENV_RESOURCE \
#  --ip-address Private \
#  --subscription $SUBSCRIPTION \
#  --registry-login-server $REGISTRY_URL \
#  --registry-username $REGISTRY_USER \
#  --registry-password $REGISTRY_PWD

# Start container instance
az container start -n $CONTAINER \
  --resource-group $RESOURCE_GROUP \
  --subscription $SUBSCRIPTION \
  --verbose --debug