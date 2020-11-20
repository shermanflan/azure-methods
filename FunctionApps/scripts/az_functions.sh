#!/bin/bash -eux

declare RESOURCE_GROUP="rkofunctionsdemo"
declare SUBSCRIPTION="Azure subscription sandbox"
declare FUNCTIONAPP="RKOIntegrationTrigger"

# az functionapp delete \
#     --name "${FUNCTIONAPP}" \
#     --resource-group "${RESOURCE_GROUP}" \
#     --subscription "${SUBSCRIPTION}"

az group delete \
    --name $RESOURCE_GROUP
