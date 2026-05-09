# Networking Module

This module provisions a standard AWS VPC with public and private subnets across multiple availability zones.

## Features
- **VPC**: Enabled with DNS support and hostnames.
- **Internet Gateway**: Attached to the VPC for public internet access.
- **Public Subnets**: Automatically maps public IPs on launch. Tagged for AWS Load Balancer Controller.
- **Private Subnets**: Isolated subnets for application and database resources.
- **NAT Gateway**: Single, cost-optimized NAT Gateway for private subnet outbound traffic.
- **Route Tables**: Configured for both public (IGW) and private (NAT) traffic flows.

## Usage

```hcl
module "networking" {
  source = "../../modules/networking"

  environment  = "dev"
  project_name = "RupeePlan"
  
  vpc_cidr            = "10.0.0.0/16"
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
  availability_zones   = ["ap-south-1a", "ap-south-1b"]
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| vpc_cidr | The CIDR block for the VPC | string | `10.0.0.0/16` | no |
| environment | Environment name (e.g. dev, prod) | string | n/a | yes |
| project_name | Project name for tagging | string | `RupeePlan` | no |
| public_subnet_cidrs | List of CIDR blocks for public subnets | list(string) | `["10.0.1.0/24", "10.0.2.0/24"]` | no |
| private_subnet_cidrs | List of CIDR blocks for private subnets | list(string) | `["10.0.11.0/24", "10.0.12.0/24"]` | no |
| availability_zones | List of availability zones | list(string) | `["ap-south-1a", "ap-south-1b"]` | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | The ID of the VPC |
| public_subnet_ids | List of IDs of public subnets |
| private_subnet_ids | List of IDs of private subnets |
| vpc_cidr_block | The CIDR block of the VPC |
