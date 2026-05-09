# Issue 5: AWS Networking Infrastructure (IaC)

## Technical Overview
In this issue, we transitioned from local Docker networking to cloud-native infrastructure using **Terraform**. We implemented a highly available, secure networking foundation on AWS.

### Key Concepts Implemented

#### 1. Multi-AZ VPC Architecture
- **Problem**: Deploying resources in a single Availability Zone (AZ) makes the application vulnerable to regional data center failures.
- **Solution**: Provision subnets across multiple AZs (Public and Private).
- **Implementation**:
    - **VPC**: A dedicated `/16` network for RupeePlan.
    - **Public Subnets**: For resources that need direct internet access (ALBs, NAT Gateways).
    - **Private Subnets**: For secure workloads (EKS nodes, RDS) that should not be reachable from the internet.

#### 2. Cost-Optimized NAT Strategy
- **Problem**: AWS charges ~$32/month per NAT Gateway. A NAT Gateway in every AZ can become expensive for a startup/dev environment.
- **Solution**: Use a single NAT Gateway in one public subnet and route all private traffic through it.
- **Trade-off**: Slightly lower availability (if that specific AZ fails, private egress is lost), but significant cost savings ($64/mo saved in a 3-AZ setup).

#### 3. Kubernetes-Specific Tagging
- **Problem**: The AWS Load Balancer Controller needs to know which subnets to use for internal vs. external load balancers.
- **Solution**: Apply specific AWS tags to subnets.
- **Tags**:
    - `kubernetes.io/role/elb = 1` (Public subnets for external LBs)
    - `kubernetes.io/role/internal-elb = 1` (Private subnets for internal LBs)
    - `kubernetes.io/cluster/<cluster-name> = shared`

---

## Interview Questions & Answers

### Q1: Why use private subnets for the database and EKS nodes?
**A**: Security. By placing these resources in private subnets, we ensure they have no public IP addresses and cannot be accessed directly from the internet. They can only communicate with the outside world via a NAT Gateway (egress only), significantly reducing the attack surface.

### Q2: What is the difference between an Internet Gateway and a NAT Gateway?
**A**: An **Internet Gateway (IGW)** allows public subnets to have two-way communication with the internet. A **NAT Gateway** allows resources in private subnets to initiate outgoing connections to the internet (e.g., to download patches or container images) while preventing the internet from initiating connections to them.

### Q3: How does Terraform manage state, and why is it important?
**A**: Terraform uses a **state file** (`terraform.tfstate`) to map your configuration to real-world resources. It allows Terraform to track what it has created, detect drift, and safely plan changes. In production, this state should be stored remotely (e.g., in S3 with DynamoDB locking).

### Q4: Explain the "Module" pattern in Terraform.
**A**: Modules allow you to package related resources into a reusable unit. This promotes the DRY (Don't Repeat Yourself) principle and allows for consistent infrastructure across different environments (dev, staging, prod) by just changing the input variables.

### Q5: What are "Route Tables" in a VPC?
**A**: Route tables contain a set of rules (routes) that determine where network traffic from your subnets or gateways is directed. For example, a public subnet's route table has a route to the Internet Gateway (`0.0.0.0/0 -> igw-id`), while a private subnet routes to the NAT Gateway.
