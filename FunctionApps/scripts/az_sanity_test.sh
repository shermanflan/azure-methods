#!/bin/bash -eux

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

echo "Topic endpoint is ${TOPIC_ENDPOINT}"
echo "Topic key is ${TOPIC_KEY}"

declare PAYLOAD='[{"id": "test-id", "data": {"tag1": "sectest1", "tag2": "value3"}, "subject": "new-job-1", "eventType": "new-job-event-1", "eventTime": "'`date +%Y-%m-%dT%H:%M:%S%z`'", "dataVersion": "1.0"}]'

echo "Sending payload"
echo ${PAYLOAD} | jq '.'
curl -X POST -H "aeg-sas-key: ${TOPIC_KEY}" -d "${PAYLOAD}" ${TOPIC_ENDPOINT}