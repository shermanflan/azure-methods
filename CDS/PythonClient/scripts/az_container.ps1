
# Start container using Powershell
#Invoke-AzureRmResourceAction `
#  -ResourceGroupName $RESOURCE_GROUP `
#  -ResourceName $CONTAINER `
#  -Action Start `
#  -Force `
#  -ResourceType Microsoft.ContainerInstance/containerGroups

# Start container using new Az module
#Invoke-AzResourceAction `
#  -Action Start -Force `
#  -ResourceGroupName $RESOURCE_GROUP `
#  -ResourceName $CONTAINER `
#  -ResourceType Microsoft.ContainerInstance/containerGroups

# Grant access to a resource
# Can be used for Function Apps for example
#New-AzRoleAssignment `
#  -ObjectId  `
#  -RoleDefinitionName Contributor `
#  -ResourceGroupName $RESOURCE_GROUP `
#  -ResourceName $CONTAINER `
#  -ResourceType Microsoft.ContainerInstance/containerGroups
