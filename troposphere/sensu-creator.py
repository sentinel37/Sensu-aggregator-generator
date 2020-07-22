#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Needs to  be Changed:                             │
# └───────────────────────────────────────────────────────────────────────────┘
#


#            VPC ID
#            VPC AZ
#            VPC Subnet
#            EC2 SG




#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Sensu Dashboard                                   │
# └───────────────────────────────────────────────────────────────────────────┘
#

#           IP Address of the Dashboard Instance:3000



#!/usr/bin/python

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Import Troposphere Modules                        │
# └───────────────────────────────────────────────────────────────────────────┘
#
from troposphere import Template, Ref, Output, Join, GetAtt, iam, Tag
from troposphere import Parameter, Tags, Base64, Sub, FindInMap
import troposphere.ec2 as ec2
from troposphere.ec2 import NetworkInterface, NetworkInterfaceProperty
from troposphere.iam import Role, InstanceProfile, Policy
from awacs.aws import Allow, Statement, Principal, PolicyDocument
from awacs.aws import Policy as AWACSPolicy
from awacs.sts import AssumeRole

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Setting Template Parameter                        │
# └───────────────────────────────────────────────────────────────────────────┘
#
template = Template()
#

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Template Description                              │
# └───────────────────────────────────────────────────────────────────────────┘
#

description = template.set_description("Sensu Demo CF Template")

TERMINATION_PROTECTION_ENABLED = template.add_parameter(Parameter(
    'TerminationProtectionEnabled',
    Description='Termination protection on CF Template.',
    Type='String',
    Default='true',
    AllowedValues=['true', 'false'],
    ))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Key Pair Selector Parameter                       │
# └───────────────────────────────────────────────────────────────────────────┘
#

#Key Pair Selector
keypair = template.add_parameter(Parameter(
    "KeyPair",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="Key Pair",
    Default=""
))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Choose Lastest AMI ID Parameter                   │
# └───────────────────────────────────────────────────────────────────────────┘
#

#Key Pair Selector
amiid = template.add_parameter(Parameter(
    "AMIID",
    Type="AWS::EC2::Image::Id",
    Description="Get the Latest AMI ID",
    Default=''

))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         VPC Parameter Parameter                           │
# └───────────────────────────────────────────────────────────────────────────┘
#

#VPC Location
vpc_param = template.add_parameter(Parameter(
    "VpcId",
    Description="Choose Desired VPC",
    Type="AWS::EC2::VPC::Id",
    Default=""

))


#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         CIDR Parameter                                    │
# └───────────────────────────────────────────────────────────────────────────┘
#

#VPC Location
cidr = template.add_parameter(Parameter(
    "VpcCIDR",
    Description= "VPC CIDR Block (eg 10.0.0.0/16)",
    Type="String",
    Default="",
    AllowedPattern= '((\d{1,3})\.){3}\d{1,3}/\d{1,2}'
))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         Subnet Selector Parameter                         │
# └───────────────────────────────────────────────────────────────────────────┘
#

#Subnet
vpc_subnet = template.add_parameter(Parameter(
    "SubnetId",
    Description="Choose Subnet",
    Type="AWS::EC2::Subnet::Id",
    Default=""

))


#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         AZ Selector Parameter                             │
# └───────────────────────────────────────────────────────────────────────────┘
#

#AZ
vpc_availibility_zone = template.add_parameter(Parameter(
    "AvailibilityZone",
    Description="Availability Zone for Monitoring Instance",
    Type="AWS::EC2::AvailabilityZone::Name",
    Default=""
))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                               EBS Volume Parameter                        │
# └───────────────────────────────────────────────────────────────────────────┘
#
sensuaggregatorebsvolumesize = template.add_parameter(Parameter(
    "SensuAggrefatorEc2VolSizeParam",
    Description="Second Volume size for for Monitoring Instance",
    Type="Number",
    Default=30
))
sensuaggregatorvolume = template.add_resource(ec2.Volume(
    "SensuAggrefatorinstancevolume",
    AvailabilityZone=Ref(vpc_availibility_zone),
    DeletionPolicy="Delete",
    Size=Ref(sensuaggregatorebsvolumesize)))


sensuebsvolumesize = template.add_parameter(Parameter(
    "SensuGeneratorEc2VolSizeParam",
    Description="Second Volume size for for Monitoring Instance",
    Type="Number",
    Default=30
))
sensuvolume = template.add_resource(ec2.Volume(
    "SensuGeneratorinstancevolume",
    AvailabilityZone=Ref(vpc_availibility_zone),
    DeletionPolicy="Delete",
    Size=Ref(sensuebsvolumesize)))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                               EBS Volume End                              │
# └───────────────────────────────────────────────────────────────────────────┘
#

#instance Type add_parameter
instancetype = template.add_parameter(Parameter(
    'InstanceType',
    Description='EC2 instance type',
    Type='String',
    Default='t2.micro',
    AllowedValues=['m5.xlarge','t2.micro'],
    ConstraintDescription='must be a valid EC2 instance type.', ))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                               EBS Volume End                              │
# └───────────────────────────────────────────────────────────────────────────┘
#
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                     Sensu Dashboard Username and Password                 │
# └───────────────────────────────────────────────────────────────────────────┘
#
#
username = template.add_parameter(Parameter(
    'Username',
    Description='Sensu Login Username (13 Characters)',
    Type='String',
    Default='admin',
    ConstraintDescription='must be a valid EC2 instance type.', ))

password = template.add_parameter(Parameter(
    'Password',
    Description='Sensu login Password (13 Characters)',
    #Type='NoEcho',
    Type='String',
    Default='admin',
    ConstraintDescription='must be a valid EC2 instance type.', ))


# ┌───────────────────────────────────────────────────────────────────────────┐
# │                     Sensu Dashboard Username and Password                 │
# └───────────────────────────────────────────────────────────────────────────┘
#
#

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                     VPC Security Group Mapping                            │
# └───────────────────────────────────────────────────────────────────────────┘
#

#

mappings = template.add_mapping('VPCDetails', {

    "VPC id":{"SenseSG":"Security Group ID"},
    })

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                     VPC Security Group End                                │
# └───────────────────────────────────────────────────────────────────────────┘
#



#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │             Create Instance Profile Role                                  │
# └───────────────────────────────────────────────────────────────────────────┘
#

# sensu_role = iam.Role(
#     'ADAUTOJOINROLE',
#     AssumeRolePolicyDocument=AWACSPolicy(
#         Statement=[
#             Statement(
#                 Effect=Allow,
#                 Action=[AssumeRole],
#                 Principal=Principal("Service", ["ec2.amazonaws.com"])
#             )]),
#     Policies=[Policy(
#         PolicyName='sensuAccess',
#         PolicyDocument=
#             {
#                 "Version": "2012-10-17",
#                 "Statement": [
# {
#             "Effect": "Allow",
#             "Action": [
#                 "ec2:DescribeTags"
#             ],
#             "Resource": "*"
#         }
#         ]}),]
#         #RoleName='MLMS-RDS-Logs-Role'
#     )
#
# sensu_role_profile = template.add_resource(iam.InstanceProfile(
#     "sensurole",
#     Roles=[Ref(sensu_role)],
#     InstanceProfileName=Join("-", [Ref(sensu_role), "profile"])
# ))


#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                    Sensu Aggregator Instance Configuration                │
# └───────────────────────────────────────────────────────────────────────────┘
#
instance = ec2.Instance("SensuAggregatorBOX")
instance.ImageId = Ref(amiid)
instance.InstanceType = Ref(instancetype)
instance.KeyName = Ref(keypair)
instance.Tags=[
    Tag("Name","Sensu-Aggregator-Box"),
    Tag("JIRA TICKET NUMBER:","###"),
    Tag("Developers","Dev Team"),
]

#instance.IamInstanceProfile=Ref(sensu_role_profile)
instance.AvailabilityZone=Ref(vpc_availibility_zone)
instance.SubnetId=Ref(vpc_subnet)
instance.SecurityGroupIds=[FindInMap("VPCDetails", Ref(vpc_param), "SenseSG")]
instance.Volumes=[ec2.MountPoint(Device="xvdf",VolumeId=Ref(sensuaggregatorvolume))]


#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                    Sensu Geberator Instance Configuration                 │
# └───────────────────────────────────────────────────────────────────────────┘
#
instance1 = ec2.Instance("SensuGeneratorBOX")
instance1.ImageId = Ref(amiid)
instance1.InstanceType = Ref(instancetype)
instance1.KeyName = Ref(keypair)
instance1.Tags=[
    Tag("Name","Sensu-Data-Generator-Box"),
    Tag("JIRA TICKET NUMBER:","###"),
    Tag("Developers","Dev Team"),
]

instance1.AvailabilityZone=Ref(vpc_availibility_zone)
instance1.SubnetId=Ref(vpc_subnet)
instance1.SecurityGroupIds=[FindInMap("VPCDetails", Ref(vpc_param), "SenseSG")]
instance1.Volumes=[ec2.MountPoint(Device="xvdf",VolumeId=Ref(sensuvolume))]

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                         EC2 User Data                                     │
# └───────────────────────────────────────────────────────────────────────────┘
#
instance.UserData=Base64(Join('',
[
'#!/bin/bash -xe\n',
#'yum -y update\n',
########----------------------------Install Sensu--------------------------------------------------------########------------------------------------------------------------------------------------########------------------------------------------------------------------------------------########------------------------------------------------------------------------------------########------------------------------------------------------------------------------------
'curl -s https://packagecloud.io/install/repositories/sensu/stable/script.rpm.sh | sudo bash\n',
'sudo yum install sensu-go-backend -y; sudo curl -L https://docs.sensu.io/sensu-go/latest/files/backend.yml -o /etc/sensu/backend.yml;\n',
'sudo service sensu-backend start; service sensu-backend status;\n',
'export SENSU_BACKEND_CLUSTER_ADMIN_USERNAME=',Ref(username), '; export SENSU_BACKEND_CLUSTER_ADMIN_PASSWORD=',Ref(password),';sensu-backend init;\n',
'curl https://packagecloud.io/install/repositories/sensu/stable/script.rpm.sh | sudo bash;sudo yum install sensu-go-cli -y;\n',
'sensuctl configure -n --username ',Ref(username),' --password ',Ref(password),' --namespace default --url \'http://127.0.0.1:8080\'\n',
'\n',
]))


instance1.UserData=Base64(Join('',
[
'#!/bin/bash -xe\n',
#'yum -y update\n',
'echo "----------------Starting install process--------------------">>/home/ec2-user/install.txt\n',
'echo "----------------Starting install process--------------------">>/home/ec2-user/install.txt\n',
'echo "----------------Starting install process--------------------">>/home/ec2-user/install.txt\n',
'echo "----------------Starting install process--------------------">>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "********************* Installed wget ************************">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'yum -y install wget>>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "********************* Installed RMP Script ******************">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'curl -s https://packagecloud.io/install/repositories/sensu/stable/script.rpm.sh | sudo bash>>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "*********************** Install Sensu Agent *****************">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'sudo yum install sensu-go-agent -y>>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "************************** Installation Repo Set up *********">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'curl https://packagecloud.io/install/repositories/sensu/stable/script.rpm.sh | sudo bash>>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "************************** Install Sense CLI ****************">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'sudo yum install sensu-go-cli -y>>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "************************* Configure Sensu *******************">>/home/ec2-user/install.txt\n',
'echo "*************************************************************">>/home/ec2-user/install.txt\n',
'echo "">>/home/ec2-user/install.txt\n',
'sensuctl configure -n --username ',Ref(username),' --password ',Ref(password),' --namespace default --url \'http://',GetAtt(instance, "PublicIp"),':8080\'\n',
'sudo curl -L https://docs.sensu.io/sensu-go/latest/files/agent.yml --create-dirs -o /etc/sensu/agent.yml\n',
'cp /etc/sensu/agent.yml /etc/sensu/agent.yml.bak\n',
'echo "*************************** Uncomment backend url **********************">>/home/ec2-user/install.txt\n',
'sed -i \'s/#backend-url:/backend-url:/g\' /etc/sensu/agent.yml\n',
'echo "*************************** Update Dashboard IP **********************">>/home/ec2-user/install.txt\n',
#'sed \'/backend-url:/a   - "ws://',GetAtt(instance, "PublicIp"),':8081\' /etc/sensu/agent.yml \n'
#'sed -i \'s/#  - "ws://127.0.0.1:8081"/  - \"ws://',GetAtt(instance, "PublicIp"),':8081"/g\'  /etc/sensu/agent.yml\n',
'sed -i \'s/127.0.0.1/',GetAtt(instance, "PublicIp"),'/g\' /etc/sensu/agent.yml\n',
'sed -i \'s/#  - "/  - "/1\' /etc/sensu/agent.yml\n',
'echo "*************************** Update Username **********************">>/home/ec2-user/install.txt\n',
'sed -i \'s/#user: \"agent\"/user: \"',Ref(username),'"/g\' /etc/sensu/agent.yml\n',
'echo "*************************** Update Password **********************">>/home/ec2-user/install.txt\n',
'sed -i \'s/#password: \"P@ssw0rd!\"/password: "',Ref(password),'"/g\' /etc/sensu/agent.yml\n',
'echo "*************************** Start Agent **********************">>/home/ec2-user/install.txt\n',
'systemctl start sensu-agent\n',
'systemctl enable sensu-agent\n',
'echo "*************************** Download Helper **********************">>/home/ec2-user/install.txt\n',
'wget -O /usr/local/bin/sensu-shell-helper https://raw.githubusercontent.com/solarkennedy/sensu-shell-helper/master/sensu-shell-helper\n',
'echo "*************************** change permissions **********************">>/home/ec2-user/install.txt\n',
'chmod +x /usr/local/bin/sensu-shell-helper\n',
'echo "*************************** Create Script **********************">>/home/ec2-user/install.txt\n',
#######################################################################################################################
'''
cat << EOF > /usr/local/bin/open-port
#!/bin/bash
var=\$(sudo netstat -tulpn | grep LISTEN | awk '{print \$4}' |awk -F: '{print \$2}')
echo "Open ports are:" \$var
exit 0
EOF
'''
#######################################################################################################################
'echo "*************************** Change Permissions **********************">>/home/ec2-user/install.txt\n',
'chmod +x /usr/local/bin/open-port\n',
'echo "*************************** Test Script **********************">>/home/ec2-user/install.txt\n',
'/usr/local/bin/sensu-shell-helper /usr/local/bin/open-port\n',
'/usr/local/bin/sensu-shell-helper /usr/local/bin/open-port\n',
'echo "*************************** Create Cron **********************">>/home/ec2-user/install.txt\n',
'echo "*/30 * * * * /usr/local/bin/sensu-shell-helper /usr/local/bin/open-port" >> /var/spool/cron/root\n',
'\n',
]))


#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                   Adding Instances to Template                            │
# └───────────────────────────────────────────────────────────────────────────┘
#
template.add_resource(instance)
template.add_resource(instance1)
#template.add_resource(sensu_role)

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                  CF Template Output Selected Options                      │
# └───────────────────────────────────────────────────────────────────────────┘
#
template.add_output(Output(
    "SenseAggregatorInstancePublicIP",
    Description="Sense Aggregator Instance Public IP",
    Value=GetAtt(instance, "PublicIp"),
))

template.add_output(Output(
    "SenseAggregatorInstancePublicDNS",
    Description="Sense Aggregator Instance Public DNS Name",
    Value=GetAtt(instance, "PublicDnsName"),
))

template.add_output(Output(
    "SenseAggregatorInstancePrivateIP",
    Description="Sense Aggregator Instance Private IP",
    Value=GetAtt(instance, "PrivateIp")
))

#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                             Export to YAML                                │
# └───────────────────────────────────────────────────────────────────────────┘
#
print (template.to_yaml())
# ec2-metadata |grep 'aws route53 change-resource-record-sets'
