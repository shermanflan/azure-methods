#!/bin/bash

echo "Cleaning up ${RESOURCE_GROUP}"
az group delete \
    --name "${RESOURCE_GROUP}"

# az functionapp delete \
#     --name "${FUNCTIONAPP}" \
#     --resource-group "${RESOURCE_GROUP}" \
#     --subscription "${SUBSCRIPTION}"
