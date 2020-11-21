#!/bin/bash -eux

declare RESOURCE_GROUP="rko-functions-demo"
declare SUBSCRIPTION="Azure subscription sandbox"
declare LOCATION="eastus"
declare FUNCTIONAPP="RKOIntegrationTrigger"
declare EVENT_GRID_TOPIC="batch-jobs-topic"
declare EVENT_GRID_SUBSCRIPTION="batch-jobs-subscription"

# declare ENDPOINT=$(az eventgrid topic show --name ${EVENT_GRID_TOPIC} -g ${RESOURCE_GROUP} --query "endpoint" --output tsv)
# declare KEY=$(az eventgrid topic key list --name ${EVENT_GRID_TOPIC} -g ${RESOURCE_GROUP} --query "key1" --output tsv)
# echo "${ENDPOINT}: ${KEY}"

# echo "Creating resource group $RESOURCE_GROUP"
# az group create \
#     --name $RESOURCE_GROUP \
#     --location $LOCATION

# echo "Creating event grid topic"
# az eventgrid topic create \
#     --location "${LOCATION}" \
#     --name "${EVENT_GRID_TOPIC}" \
#     --resource-group "${RESOURCE_GROUP}" \
#     --subscription "${SUBSCRIPTION}" \
#     --input-schema eventgridschema \
#     --sku basic \
#     --public-network-access disabled

    # --identity {noidentity, systemassigned}
    # --inbound-ip-rules
    # --input-mapping-default-values
    # --input-mapping-fields
    # --public-network-access {disabled, enabled}
    # --tags

# declare TOPIC_ID=$(az eventgrid topic show \
#                     --name "${EVENT_GRID_TOPIC}" \
#                     --resource-group "${RESOURCE_GROUP}" \
#                     --subscription "${SUBSCRIPTION}" | jq -r '.id')
# echo "Creating event grid subscription for ${TOPIC_ID}"
# az eventgrid event-subscription create \
#     --name "${EVENT_GRID_SUBSCRIPTION}" \
#     --subscription "${SUBSCRIPTION}" \
#     --endpoint
#     --endpoint-type azurefunction \
#     --event-delivery-schema eventgridschema \
#     --source-resource-id "${TOPIC_ID}"

    # --delivery-identity {systemassigned}
    # --delivery-identity-endpoint
    # --delivery-identity-endpoint-type azurefunction \
    # --advanced-filter
    # --azure-active-directory-application-id-or-uri
    # --azure-active-directory-tenant-id
    # --deadletter-endpoint
    # --deadletter-identity {systemassigned}
    # --deadletter-identity-endpoint
    # --event-ttl
    # --expiration-date
    # --included-event-types
    # --labels
    # --max-delivery-attempts
    # --max-events-per-batch
    # --preferred-batch-size-in-kilobytes
    # --source-resource-id
    # --subject-begins-with
    # --subject-case-sensitive {false, true}
    # --subject-ends-with

echo "Cleaning up ${RESOURCE_GROUP}"
az group delete \
    --name "${RESOURCE_GROUP}"

# az functionapp delete \
#     --name "${FUNCTIONAPP}" \
#     --resource-group "${RESOURCE_GROUP}" \
#     --subscription "${SUBSCRIPTION}"
