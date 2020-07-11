### Sensu AWS Terraform Deployment

This Terraform configuration will deploy two Sensu instances within AWS. One will be a aggregator of all instance metrics and the other will be a data generator. The Sensu Dasboard, from the Sensu aggregator instance, will monitor open ports every minutes and check if the instance is running every 20 seconds.

|Sensu Configuration|
|--------|----------|
