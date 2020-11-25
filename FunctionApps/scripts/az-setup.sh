#!/bin/bash -eux

# echo "Creating resource group $RESOURCE_GROUP"
# az group create \
#     --name $RESOURCE_GROUP \
#     --location $LOCATION

echo "Creating event grid topic"
az eventgrid topic create \
    --location "${LOCATION}" \
    --name "${EVENT_GRID_TOPIC}" \
    --resource-group "${RESOURCE_GROUP}" \
    --subscription "${SUBSCRIPTION}" \
    --input-schema eventgridschema \
    --public-network-access enabled

    # --sku premium \
    # --identity {noidentity, systemassigned}
    # --inbound-ip-rules
    # --input-mapping-default-values
    # --input-mapping-fields

declare TOPIC_ENDPOINT=$(az eventgrid topic show \
                            --name ${EVENT_GRID_TOPIC} \
                            -g ${RESOURCE_GROUP} \
                            --query "endpoint" --output tsv)
declare TOPIC_KEY=$(az eventgrid topic key list \
                        --name ${EVENT_GRID_TOPIC} \
                        -g ${RESOURCE_GROUP} \
                        --query "key1" --output tsv)
declare TOPIC_ID=$(az eventgrid topic show \
                    --name "${EVENT_GRID_TOPIC}" \
                    --resource-group "${RESOURCE_GROUP}" \
                    --subscription "${SUBSCRIPTION}" | jq -r '.id')

echo "${TOPIC_ID} created"
echo "Topic key is ${TOPIC_KEY}"

echo "Creating event grid subscription ${EVENT_GRID_SUBSCRIPTION}"
az eventgrid event-subscription create \
    --name "${EVENT_GRID_SUBSCRIPTION}" \
    --subscription "${SUBSCRIPTION}" \
    --endpoint ${FUNCTION_ENDPOINT} \
    --endpoint-type azurefunction \
    --event-delivery-schema eventgridschema \
    --source-resource-id "${TOPIC_ID}" \
    --max-delivery-attempts 3 \
    --event-ttl 3 \
    --included-event-types new-job-event-1 new-job-event-2 \
    --subject-begins-with new-job \
    --subject-case-sensitive true \
    --deadletter-endpoint ${DEAD_LETTER}

echo "Creating event grid subscription ${EVENT_GRID_SUBSCRIPTION2}"
az eventgrid event-subscription create \
    --name "${EVENT_GRID_SUBSCRIPTION2}" \
    --subscription "${SUBSCRIPTION}" \
    --endpoint ${FUNCTION_ENDPOINT2} \
    --endpoint-type azurefunction \
    --event-delivery-schema eventgridschema \
    --source-resource-id "${TOPIC_ID}" \
    --max-delivery-attempts 3 \
    --event-ttl 3 \
    --included-event-types new-job-event-3 \
    --subject-begins-with new-job-oracle \
    --subject-case-sensitive true \
    --deadletter-endpoint ${DEAD_LETTER}

    # --delivery-identity {systemassigned}
    # --delivery-identity-endpoint
    # --delivery-identity-endpoint-type azurefunction \
    # --advanced-filter
    # --azure-active-directory-application-id-or-uri
    # --azure-active-directory-tenant-id
    # --deadletter-identity {systemassigned}
    # --deadletter-identity-endpoint
    # --expiration-date
    # --max-events-per-batch
    # --preferred-batch-size-in-kilobytes
    # --subject-ends-with
