#!/bin/bash -eux

declare RESOURCE_GROUP=""
declare SUBSCRIPTION=""
declare FUNCTIONAPP="RKOIntegrationTrigger"

az functionapp delete \
    --name $FUNCTIONAPP \
    --resource-group $RESOURCE_GROUP \
    --subscription $SUBSCRIPTION

