# Create IAM Policy for deployment by pike

## System

### Requirements

- Terraform = 1.7.2
- aws-cli >= 1.27.X

## Deploy

### Install tools

Install serverless, python venv and terraform on mac

```bash
# At project root dir
cd (project_root/)serverless
python -m venv .venv

brew install tfenv
tfenv install 1.7.2
tfenv use 1.7.2
```

### Install Packages

### Deploy AWS Resources by Terraform

#### 1. Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform-iam-role
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

### 2. Set AWS Profile

##### If use aws profile

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_REGION="ap-northeast-1"
```

##### if use aws-vault

```bash
export AWS_REGION="ap-northeast-1"
aws-vault exec your-aws-role-for-create-iam-policy
```

The role needs below policies

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:GetPolicy",
        "iam:CreatePolicy",
        "iam:DeletePolicy",
        "iam:CreatePolicyVersion",
        "iam:DeletePolicyVersion",
        "iam:SetDefaultPolicyVersion",
        "iam:ListPolicyVersions",
        "iam:GetPolicyVersion"
      ],
      "Resource": ["arn:aws:iam::your-aws-account-number:policy/*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListPolicies",
        "iam:ListAttachedRolePolicies",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy"
      ],
      "Resource": ["arn:aws:iam::your-aws-account-number:role/*"]
    }
  ]
}
```

### 3. Execute terraform init

```bash
terraform init
```

### 4. Execute terraform apply

```bash
terraform apply -auto-approve -var-file=./terraform.tfvars
```

## For Development

If you need to create definition, execute as below

Install pike on mac

```bash
brew tap jameswoolfenden/homebrew-tap
brew install jameswoolfenden/tap/pike
```

Create Terraform file to create IAM policy

```bash
cd (project_root_dir)/terraform
pike scan -d . -i -e > ../terraform-iam-role/main.tf
```

Edit generated file

```bash
cd ../terraform-iam-role
vi main.tf
```

Add below policy to `main.tf`, because pike does not generate policy for RDS Proxy (pile version v0.3.6)

```terraform
      {
        "Sid" : "VisualEditor9",
        "Effect" : "Allow",
        "Action" : [
          "rds:CreateDBProxy",
          "rds:DeleteDBProxy",
          "rds:ModifyDBProxy",
          "rds:RegisterDBProxyTargets",
          "rds:DeregisterDBProxyTargets",
          "rds:DescribeDBProxies",
          "rds:CreateDBProxyEndpoint",
          "rds:DeleteDBProxyEndpoint",
          "rds:ModifyDBProxyEndpoint",
          "rds:DescribeDBProxyEndpoints"
        ],
        "Resource" : [
          "arn:aws:rds:ap-northeast-1:your-aws-account-number:db-proxy:*"
        ]
      }
```

And Edit other Action and Resource for your env
