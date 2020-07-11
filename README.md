### Sensu AWS Terraform Deployment

This Terraform configuration will deploy two Sensu instances within AWS. One will be a aggregator of all instance metrics and the other will be a data generator. The Sensu Dasboard, from the Sensu aggregator instance, will monitor open ports every minutes and check if the instance is running every 20 seconds.

|Sensu Configuration|
|--------|----------|
|Access Key|Line 9|
|Secret Key|Line 10|
|Key Name|Line 15 and 36|
|AMI ID| Line 13 and 34|
|Subnet ID|Line 16 and 37|
