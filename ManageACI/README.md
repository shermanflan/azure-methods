# Manage Azure Container Instances
Example using the Azure management API to create and delete an ACI.

## Features
- Reads ACI configuration from a standard ACI YAML file
- Uses the 
[`AzureOperationPoller`](https://docs.microsoft.com/en-us/python/api/msrestazure/msrestazure.azure_operation.azureoperationpoller?view=azure-python) 
to delete the ACI after successful provisioning

## References
Inspired by the [Azure Samples](https://github.com/Azure-Samples/aci-docs-sample-python/blob/master/src/aci_docs_sample.py)

## Notes
- The reference Azure sample [code](https://github.com/Azure-Samples/aci-docs-sample-python/blob/master/src/aci_docs_sample.py) 
does not work with the latest version of the `azure-mgmt-resource` library. Be sure to pin it at version 10.0.0 
or below to get the sample code to work.