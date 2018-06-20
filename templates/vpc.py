from troposphere import (
    Output,
    Sub,
    Select,
    GetAZs,
    Parameter,
    Ref,
    Template
)
from troposphere.ec2 import (
    VPC,
    SubnetRouteTableAssociation,
    InternetGateway,
    VPCGatewayAttachment,
    Subnet,
    Route,
    RouteTable
)
t = Template()

t.add_description(
    "Create VPC resources for Blue/Green Deployment on ECS. For further reference, please review BluegreenRepo ==> https://github.com/awslabs/ecs-blue-green-deployment",
)
Name = t.add_parameter(Parameter(
    "Name",
    Type="String"
))
VpcCIDR = t.add_parameter(Parameter(
    "VpcCIDR",
    Type="String"
))
Subnet1CIDR = t.add_parameter(Parameter(
    "Subnet1CIDR",
    Type="String"
))
Subnet2CIDR = t.add_parameter(Parameter(
    "Subnet2CIDR",
    Type="String"
))

# Resources
VPC = t.add_resource(VPC(
    "VPC",
    CidrBlock=Ref(VpcCIDR),
    Tags=[{"Key": "Name", "Value": Ref(Name)}]
))
InternetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=[{"Key": "Name", "Value": Ref(Name)}]
))
InternetGatewayAttachment = t.add_resource(VPCGatewayAttachment(
    "InternetGatewayAttachment",
    InternetGatewayId=Ref(InternetGateway),
    VpcId=Ref(VPC)
))
Subnet1 = t.add_resource(Subnet(
    "Subnet1",
    VpcId=Ref(VPC),
    CidrBlock=Ref(Subnet1CIDR),
    AvailabilityZone=Select("0", GetAZs()),
    Tags=[{"Key": "Name", "Value": Sub([Name, "Public"])}]
))
Subnet2 = t.add_resource(Subnet(
    "Subnet2",
    VpcId=Ref(VPC),
    CidrBlock=Ref(Subnet2CIDR),
    AvailabilityZone=Select("1", GetAZs()),
    Tags=[{"Key": "Name", "Value": Sub([Name, "Public"])}]
))
RouteTable = t.add_resource(RouteTable(
    "RouteTable",
    VpcId=Ref(VPC),
    Tags=[{"Key": "Name", "Value": Ref(Name)}]
))
DefaultRoute = t.add_resource(Route(
    "DefaultRoute",
    RouteTableId=Ref(RouteTable),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(InternetGateway)
))
Subnet1RouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "Subnet1RouteTableAssociation",
    RouteTableId=Ref(RouteTable),
    SubnetId=Ref(Subnet1)
))
Subnet2RouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "Subnet2RouteTableAssociation",
    RouteTableId=Ref(RouteTable),
    SubnetId=Ref(Subnet2)
))

Outputs = t.add_output([
    Output("Subnet1", Value=Ref(Subnet1)),
    Output("Subnet2", Value=Ref(Subnet2)),
    Output("VPC", Value=Ref(VPC))
])
template = (t.to_yaml())

if __name__ == "__main__":
    print(template)
    with open("vpc_new.yaml", 'w+') as f:
        f.write(template)

