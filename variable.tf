data "template_file" "init" {
  vars = {
    address = "${aws_instance.Sensu-Aggregator.public_ip}"
  }
}
