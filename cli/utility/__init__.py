import json
import os

AZ_SUBSCRIPTION = os.environ.get("AZURE_SUBSCRIPTION", "")
AZ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "")
AZ_LOG_WORKSPACE = os.environ.get("AZ_LOG_WORKSPACE", "")
DIAGNOSTIC_NAME = os.environ.get("DIAGNOSTIC_NAME", "diagnostic-auto-setup")
SCRIPT_HOME = os.environ.get("APP_HOME", "/home/condesa1931/personal/github/azure-methods/cli/scripts")

LOG_MAP, METRIC_MAP = {}, {}

with open(os.path.join(SCRIPT_HOME, "config-adf-log.json"), mode='rt') as f:
    LOG_MAP["Microsoft.DataFactory/factories"] = json.load(f)
with open(os.path.join(SCRIPT_HOME, "config-db-log.json"), mode='rt') as f:
    LOG_MAP["Microsoft.Sql/servers/databases"] = json.load(f)
with open(os.path.join(SCRIPT_HOME, "config-adf-metrics.json"), mode='rt') as f:
    METRIC_MAP["Microsoft.DataFactory/factories"] = json.load(f)
with open(os.path.join(SCRIPT_HOME, "config-db-metrics.json"), mode='rt') as f:
    METRIC_MAP["Microsoft.Sql/servers/databases"] = json.load(f)
