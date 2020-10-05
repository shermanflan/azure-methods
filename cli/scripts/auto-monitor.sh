#!/bin/bash

declare RESOURCE_GROUP=""
declare SUBSCRIPTION=""
declare DIAGNOSTICS_NAME="diagnostic-auto-setup"
declare EA_WORKSPACE=""
declare DB_LOG_CONFIG="$(< ~/personal/github/azure-methods/cli/scripts/config-db-log.json)"
declare DB_METRICS_CONFIG="$(< ~/personal/github/azure-methods/cli/scripts/config-db-metrics.json)"
declare ADF_LOG_CONFIG="$(< ~/personal/github/azure-methods/cli/scripts/config-adf-log.json)"
declare ADF_METRICS_CONFIG="$(< ~/personal/github/azure-methods/cli/scripts/config-adf-metrics.json)"

# Commands to inspect and automate diagnostic settings configuration.
# List resources by tag.
#az resource list \
#  --subscription "$SUBSCRIPTION" \
#  --tag 'auto-monitor=True'  # can use regex

# Retrieve all ADFs for given subscription.
#az resource list \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.DataFactory/factories" \

# Show all ADF diagnostic settings.
# If empty, returns: { "value": [] }
az monitor diagnostic-settings list \
  --resource "POCAzureMonitorADF" \
  -g "$RESOURCE_GROUP" \
  --subscription "$SUBSCRIPTION" \
  --resource-type "Microsoft.DataFactory/factories"

# Show specific ADF diagnostic settings.
# If empty, returns: "ValidationError: The diagnostic setting 'Diagnose' doesn't exist."
#az monitor diagnostic-settings show \
#  --name "$DIAGNOSTICS_NAME" \
#  --resource "POCAzureMonitorADF" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.DataFactory/factories"

# Delete ADF diagnostic setting.
#az monitor diagnostic-settings delete \
#  --name "$DIAGNOSTICS_NAME" \
#  --resource "" \

# Create ADF diagnostic setting.
# TODO: Research retention policy setting.
#az monitor diagnostic-settings create \
#  --name "$DIAGNOSTICS_NAME" \
#  --resource "" \
#  --logs "$ADF_LOG_CONFIG" \
#  --metrics "$ADF_METRICS_CONFIG" \
#  --workspace "$EA_WORKSPACE" \
#  --export-to-resource-specific "true"

# TODO: Retrieve all SQL Servers for a given subscription.
#az sql server list \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \

# Show a specific server by name.
#az sql server show \
#  --name "pocazuremonitorsql" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \

# Show a specific server's audit policy.
#az sql server audit-policy show \
#  --name "pocazuremonitorsql" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \

# NOTE: audit-policy update does not yet support Log Analytics configuration.
#az sql server audit-policy update

# Show all SQL diagnostic settings.
# If empty, returns: { "value": [] }
#az monitor diagnostic-settings list \
#  --resource "POCAzureMonitorSQLDB" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.Sql/servers/pocazuremonitorsql/databases"

# Show specific SQL diagnostic settings.
# If empty, returns: "ValidationError: The diagnostic setting 'Diagnose' doesn't exist."
#az monitor diagnostic-settings show \
#  --name "$DIAGNOSTICS_NAME" \
#  --resource "POCAzureMonitorSQLDB" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.Sql/servers/pocazuremonitorsql/databases"

# Delete SQL diagnostic setting.
#az monitor diagnostic-settings delete \
#  --name "$DIAGNOSTICS_NAME" \
#  --resource "POCAzureMonitorSQLDB" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.Sql/servers/pocazuremonitorsql/databases"

# Create SQL diagnostic setting.
# TODO: Research retention policy setting.
#az monitor diagnostic-settings create \
#  --name "$DIAGNOSTICS_NAME" \
#  --resource "" \
#  --logs "$DB_LOG_CONFIG" \
#  --metrics "$DB_METRICS_CONFIG" \
#  --workspace "$EA_WORKSPACE"
