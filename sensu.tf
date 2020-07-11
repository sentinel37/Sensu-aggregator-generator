################################################################################
#################################  USAGE  ######################################
################################################################################
###              Please update Lines 9,10,13,15,16,34,36,37


provider "aws" {
  region     = "us-east-1"
  access_key = ""
  secret_key = ""
}
resource "aws_instance" "Sensu-Aggregator" {
  ami           = "ami-098f16afa9edf40be"
  instance_type = "t2.micro"
  key_name      = ""
  subnet_id     = ""
  tags = {
    Name        = "Sensu-Aggregator"
    Environment = "Test"
  }
  user_data = <<-EOF
              #!/bin/bash
              sudo curl -s https://packagecloud.io/install/repositories/sensu/stable/script.rpm.sh | sudo bash
              sudo yum install sensu-go-backend -y
              sudo curl -L https://docs.sensu.io/sensu-go/latest/files/backend.yml -o /etc/sensu/backend.yml
              sudo service sensu-backend start
              export SENSU_BACKEND_CLUSTER_ADMIN_USERNAME=admin; export SENSU_BACKEND_CLUSTER_ADMIN_PASSWORD=admin;sensu-backend init;
              curl https://packagecloud.io/install/repositories/sensu/stable/script.rpm.sh | sudo bash;sudo yum install sensu-go-cli -y;
              sensuctl configure -n --username 'admin' --password 'admin' --namespace default --url 'http://127.0.0.1:8080'
              EOF
}

resource "aws_instance" "Sensu-Generator" {
  ami           = "ami-098f16afa9edf40be"
  instance_type = "t2.micro"
  key_name      = ""
  subnet_id     = ""
  tags = {
    Name        = "Sensu-Generator"
    Environment = "Test"
  }
  user_data = <<-EOF
              #!/bin/bash
              DashboardAddress = local.address
              curl -s https://packagecloud.io/install/repositories/sensu/stable/script.rpm.sh | sudo bash
              sudo yum install sensu-go-agent -y
              sudo yum install wget -y
              sudo curl -L https://docs.sensu.io/sensu-go/latest/files/agent.yml -o /etc/sensu/agent.yml
              sed -i 's/#password: "P@ssw0rd!"/password: "admin"/g' /etc/sensu/agent.yml
              sed -i 's/#user: "agent"/user: "admin"/g' /etc/sensu/agent.yml
              sed -i 's/#backend-url:/backend-url:/g' /etc/sensu/agent.yml
              sed -i 's/#  - "ws/ - "ws/g' /etc/sensu/agent.yml
              sed -i 's/127.0.0.1/${aws_instance.Sensu-Aggregator.public_ip}/g' /etc/sensu/agent.yml
              service sensu-agent start
              wget -O /usr/local/bin/sensu-shell-helper https://raw.githubusercontent.com/solarkennedy/sensu-shell-helper/master/sensu-shell-helper
              chmod +x /usr/local/bin/sensu-shell-helper
              echo "#!/bin/bash">>/usr/local/bin/sensu.sh
              echo "sens=\$(netstat -tulpn | grep LISTEN | awk '{ print \$4 }' |awk -F':' '{print \$2}')">>/usr/local/bin/sensu.sh
              echo "echo \"The open ports on this instance are \"\$sens">>/usr/local/bin/sensu.sh
              echo "exit 0">>/usr/local/bin/sensu.sh
              chmod +x /usr/local/bin/sensu.sh
              echo '  *  *  *  *  * root /usr/local/bin/sensu-shell-helper /usr/local/bin/sensu.sh'>>/etc/crontab
              EOF
}

############################# Not needed for the code #################################
#Setting Output for Aggregator IP Address
output "Aggregator" {
  value = aws_instance.Sensu-Aggregator.public_ip
}
output "Generator" {
  value = aws_instance.Sensu-Generator.public_ip
}
# Command to use on CLI: terraform output ip


############################# Not needed for the code #################################
