#!/bin/bash -eux

echo "Create storage queue ${QUEUE_NAME}"
az storage queue create \
  --name "${QUEUE_NAME}" \
  --account-key "${STORAGE_KEY}" \
  --account-name "${STORAGE_ACCOUNT}" \
  --fail-on-exist \
  --subscription "${SUBSCRIPTION}"

#                        [--auth-mode {key, login}]
#                        [--connection-string]
#                        [--metadata]
#                        [--sas-token]
#                        [--timeout]

#echo "Build and publish docker image $IMAGE to $REGISTRY"
#az acr build \
#  --registry $REGISTRY \
#  --image $IMAGE .

#echo "Create container group $CONTAINER_GROUP using YAML file"
#az container create \
#  --resource-group "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --file "$YAML_CONFIG" \
#  --verbose

#echo "Start container $CONTAINER_GROUP"
#az container start -n "$CONTAINER_GROUP" \
#  --resource-group "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --verbose --debug

#echo "Follow logs for container $CONTAINER_GROUP"
#az container logs \
#  --resource-group "$RESOURCE_GROUP" \
#  --name "$CONTAINER_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --follow

# Assign security role to a principal.
#az role assignment create \
#  --role Contributor \
#  --assignee $PRINCIPAL \
#  --subscription $SUBSCRIPTION \
#  --scope $APP_SCOPE

# TODO: Clean up resources
#az container delete \
#  --name $CONTAINER_GROUP \
#  --resource-group $RESOURCE_GROUP \
#  --subscription $SUBSCRIPTION
