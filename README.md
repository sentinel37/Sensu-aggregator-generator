### Sensu AWS Terraform Deployment

This Terraform configuration will deploy two Sensu instances within AWS. One will be a aggregator of all instance metrics and the other will be a data generator. The Sensu Dasboard, from the Sensu aggregator instance, will monitor open ports every minutes and check if the instance is running every 20 seconds.

### sensu.tf configuration
|Variable|Location|
|--------|----------|
|Access Key|Line 4|
|Secret Key|Line 5|
|Key Name|Line 56 and 78|
|AMI ID| Line 54 and 76|
|Public Subnet ID|Line 57 and 79|
|VPC ID|Line 11|


### Usage:
  1. Clone repo
  2. cd into repo directory
  3. "terraform init"
  4. Update sensu.tf with the sensu.tf configuration table listed above
  5. "terraform validate"
  6. "terraform apply"
  7. Within web browser navigate to: http://\<sensu-aggretator public ip\>:3000


Sensu Documentation:
https://docs.sensu.io/sensu-go/latest/
