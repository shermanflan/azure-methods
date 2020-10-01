#!/bin/bash

declare RESOURCE_GROUP=""
declare SUBSCRIPTION=""
declare DIAGNOSTICS_NAME="diagnostic-auto-setup"
declare EA_WORKSPACE="poc-loganalytics-ea"
declare DB_LOG_CONFIG="$(< config-db-log.json)"
declare DB_METRICS_CONFIG="$(< config-db-metrics.json)"

# Commands to inspect and automate diagnostic settings configuration.

# TODO: Retrieve all ADFs for given subscription.
az resource list \
  -g "$RESOURCE_GROUP" \
  --subscription "$SUBSCRIPTION" \
  --resource-type "Microsoft.DataFactory/factories"

# Show all ADF diagnostic settings.
# If empty, returns: { "value": [] }
#az monitor diagnostic-settings list \
#  --resource "POCAzureMonitorADF" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.DataFactory/factories"

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
#  --resource "POCAzureMonitorADF" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.DataFactory/factories"

# Create ADF diagnostic setting.
# TODO: Research retention policy setting.
#az monitor diagnostic-settings create \
#  --name "$DIAGNOSTICS_NAME" \
#  --resource "POCAzureMonitorADF" \
#  --export-to-resource-specific "true" \
#  --logs "$(< config-adf-log.json)" \
#  --metrics "$(< config-adf-metrics.json)" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.DataFactory/factories" \
#  --workspace "$EA_WORKSPACE"

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

# TODO: Retrieve all SQL Databases for a given subscription.
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
#  --resource "POCAzureMonitorSQLDB" \
#  --logs "$DB_LOG_CONFIG" \
#  --metrics "$DB_METRICS_CONFIG" \
#  -g "$RESOURCE_GROUP" \
#  --subscription "$SUBSCRIPTION" \
#  --resource-type "Microsoft.Sql/servers/pocazuremonitorsql/databases" \
#  --workspace "$EA_WORKSPACE"
