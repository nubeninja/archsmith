module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "private_a" {
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-west-1a"
}

resource "aws_subnet" "private_b" {
  cidr_block = "10.0.2.0/24"
}

resource "aws_eks_cluster" "this" {
  name = "demo"
}
