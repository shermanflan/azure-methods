#!/bin/bash -eux

declare CONTAINER="pah-cds-python"
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
declare YAML_CONFIG=~/Personal/github/azure-methods/CDS/PythonClient/scripts/cds-python.yml
declare DB_DRIVER="{ODBC Driver 17 for SQL Server}"
declare DB_SERVER=""
declare DB=""
declare DB_USER=""
declare DB_PWD=""

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

# Create new container group
#az container create \
#  --resource-group $RESOURCE_GROUP \
#  --name $CONTAINER \
#  --image $REGISTRY_URL/$IMAGE \
#  -l "$LOCATION" \
#  --os-type Linux --cpu 1 --memory 1.5 \
#  --restart-policy Never \
#  --environment-variables \
#    AAD_TENANT=$ENV_TENANT \
#    AAD_CLIENT=$ENV_CLIENT \
#    AAD_RESOURCE=$ENV_RESOURCE \
#    DB_DRIVER="$DB_DRIVER" \
#    DB_SERVER=$DB_SERVER \
#    DB=$DB \
#  --secure-environment-variables \
#    AAD_SECRET=$ENV_SECRET \
#    DB_USER=$DB_USER \
#    DB_PWD="$DB_PWD" \
#  --ip-address Private \
#  --subscription $SUBSCRIPTION \
#  --registry-login-server $REGISTRY_URL \
#  --registry-username $REGISTRY_USER \
#  --registry-password $REGISTRY_PWD

# Alternative using YAML file.
#az container create \
#  --resource-group $RESOURCE_GROUP \
#  --file $YAML_CONFIG

# Start container instance
az container start -n $CONTAINER \
  --resource-group $RESOURCE_GROUP \
  --subscription $SUBSCRIPTION \
  --verbose --debug

# Assign security role to a principal.
#az role assignment create \
#  --role Contributor \
#  --assignee $PRINCIPAL \
#  --subscription $SUBSCRIPTION \
#  --scope $APP_SCOPE