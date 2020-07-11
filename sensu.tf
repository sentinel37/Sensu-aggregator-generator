
provider "aws" {
  region     = "us-east-1"
  access_key = ""
  secret_key = ""
}

resource "aws_security_group" "sensu-sg" {
  name        = "Sensu-SecurityGroup"
  description = "Sensu Security Group"
  vpc_id      = ""

  ingress {
    description = "Sensu Protocal"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Sensu Protocal"
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Generator Connections to Dashboard"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Generator Connections to Dashboard"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Sensu_SG"
  }
}

resource "aws_instance" "Sensu-Aggregator" {
  ami             = ""
  instance_type   = "t2.micro"
  key_name        = ""
  subnet_id       = ""
  security_groups = ["${aws_security_group.sensu-sg.id}"]
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
  ami             = ""
  instance_type   = "t2.micro"
  key_name        = ""
  subnet_id       = ""
  security_groups = ["${aws_security_group.sensu-sg.id}"]
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
output "Sensu_Aggregator" {
  value = aws_instance.Sensu-Aggregator.public_ip
}
output "Sensu_Generator" {
  value = aws_instance.Sensu-Generator.public_ip
}
output "Sensu_SG_ID" {
  value = aws_security_group.sensu-sg.id
}
# Command to use on CLI: terraform output ip


############################# Not needed for the code #################################
