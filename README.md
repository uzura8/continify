# Serverless-CMS

Constructed by

- Serverside:
  - Flask + Lambda + APIGateway (deploy by Serverless Framework)
  - DynamoDB
- Frontend: VueJS

## Instration

#### Preparation

You need below

- common
  - aws-cli = 1.29.X
  - Terraform = 1.7.2
- serverless
  - nodeJS = 20.X
  - Python = 3.10.X
- frontend
  - nodeJS = 20.X

#### Install tools

Install python venv and terraform on mac

```bash
# At project root dir
cd (project_root/)serverless
npm install serverless
python -m venv .venv
```

```bash
brew install tfenv
tfenv install 1.7.2
tfenv use 1.7.2
```

### Install Packages

Install npm packages

```bash
# At project root dir
cd (project_root/)serverless
npm install
```

Install python packages

```bash
. .venv/bin/activate
pip install -r requirements.txt
```

#### Use Contact component

If use Contact component, execute bellow

```bash
. .venv/bin/activate
pip install -r pytz Flask-WTF
```

### Create IAM Policy and Atach to Role

#### Create Role for Deployment

- Create Role for deployment by AWS Console or aws-cli
- name example: `prj-name-dev-deploy-tf-sls-role`
- Set "信頼関係" as below

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::your-aws-account-number:user/admin-base-user"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

#### Set AWS Role for Create IAM Policy

##### If use aws profile

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-role-for-create-iam-policy
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
      "Resource": ["arn:aws:iam::your-account-number:policy/*"]
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
      "Resource": ["arn:aws:iam::your-account-number:role/*"]
    }
  ]
}
```

#### Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform-iam-role
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

#### Execute terraform apply

```bash
terraform init -backend-config="region=ap-northeast-1" -backend-config="profile=your-aws-profile-name"
terraform apply -auto-approve -var-file=./terraform.tfvars
```

## Deploy AWS Resources by Terraform

### Create AWS S3 Bucket for terraform state and frontend config

Create S3 Buckets like below in ap-northeast-1 region

- **your-serverless-deployment**
  - Store deployment state files by terraformand and serverless framework
  - Create directory "terraform/your-project-name"
- **your-serverless-configs**
  - Store config files for app
  - Create directory "your-project-name/frontend/prd" and "your-project-name/frontend/dev"

#### 1. Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

#### 2. Set AWS profile name to environment variable

##### If use aws profile

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_REGION="ap-northeast-1"
```

##### if use aws-vault

```bash
export AWS_REGION="ap-northeast-1"
aws-vault exec your-aws-role-for-deploy
```

#### 3. Execute terraform init

Command Example to init

```bash
terraform init -backend-config="bucket=your-deployment" -backend-config="key=terraform/your-project/terraform.tfstate" -backend-config="region=ap-northeast-1" -backend-config="profile=your-aws-profile-name"
```

#### 4. Execute terraform apply

```bash
terraform apply -auto-approve -var-file=./terraform.tfvars
```

#### 5. Create Admin User

Create Admin User by aws-cli

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_DEFAULT_REGION="ap-northeast-1"

aws cognito-idp admin-create-user \
--user-pool-id ap-northeast-1_xxxxxxxxx \
--username your-username \
--user-attributes \
  Name=email,Value=sample@example.com \
  Name=email_verified,Value=True \
  Name=custom:role,Value=admin \
  Name=custom:acceptServiceIds,Value=hoge \
--desired-delivery-mediums EMAIL
```

You get temporary password by email
Update password as parmanent

```bash
aws cognito-idp admin-set-user-password \
--user-pool-id ap-northeast-1_xxxxxxxxx \
--username your-username \
--password 'your-parmanent-password' \
--permanent
```

#### 6. Set CORS of media file bucket

- Access to S3 console of media file bucket
- Select tab "Permission"
- Press "Edit" button of "Cross-origin resource sharing (CORS)"
- Set bellow

```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "PUT",
            "POST",
            "DELETE",
            "GET"
        ],
        "AllowedOrigins": [
            "https://your-domain.example.com"
        ],
        "ExposeHeaders": []
    }
]
```

## DynamoDB Backup Settings

If you want to backup DynamoDB items, set bellows

- Access to "AWS Backup" on AWS Console and set region
- Press "Create backup plan"
- Input as follows for "Plan"
  - Start options
    - Select "Build a new plan"
    - Backup plan name: your-project-dynamodb-backup
  - Backup rule configuration
    - Backup vault: Default
    - Backup rule name: your-project-dynamodb-backup-rule
    - Backup frequency: Daily
    - Backup window: Customize backup window
    - Backup window settings: as you like
  - Press "Create backup plan"
- Input as follows for "Assign resources"
  - General
    - Resource assignment name: your-project-dynamodb-backup-assignment
    - IAM role: Default role
  - Resource selection
    - 1. Define resource selection: Include specific resource types
    - 2. Select specific resource types: DynamoDB
      - Table names: All tables
    - 4. Refine selection using tags
      - Key: backup
      - Condition for value: Eauqls
      - Value: aws-backup
  - Press "Assign resources"

## Deploy Server Side Resources

### Setup configs

Setup config files per stage

```bash
cd (project_root/)serverless
cp -r config/stages-sample config/stages
vi config/stages/*
```

### Create Domains for API

Execute below command

```bash
npx sls create_domain --stage target-stage --verbose
```

### Deploy to Lambda

Execute below command

```bash
npx sls deploy --stage target-stage --verbose
```

## Deploy Frontend Resources

### Setup about TinyMCE Editor

- Access to [TinyMCE Dashbord](https://www.tiny.cloud/my-account/dashboard/)
- Get Your Tiny API Key
- Move to [Approved Domains](https://www.tiny.cloud/my-account/domains/), then Add your static-site domain

### Set enviroment variables

- Access to https://github.com/{your-account}/{repository-name}/settings/secrets/actions
- Push "New repository secret"
- Add Below on "Secret" tab
  - Common
    - **AWS_ACCESS_KEY_ID** : your-aws-access_key
    - **AWS_SECRET_ACCESS_KEY** : your-aws-secret_key
- Add Below on "Variables" tab
  - For Production
    - **CLOUDFRONT_DISTRIBUTION** : your cloudfront distribution created by terraform for production
    - **S3_CONFIG_BUCKET**: "your-serverles-configs/your-project/frontend/prd" for production
    - **S3_RESOURCE_BUCKET**: "your-domain-static-site.example.com" for production
  - For Develop
    - **CLOUDFRONT_DISTRIBUTION_DEV** : your cloudfront distribution created by terraform for develop
    - **S3_CONFIG_BUCKET_DEV**: "your-serverles-configs/your-project/frontend/dev" for develop
    - **S3_RESOURCE_BUCKET_DEV**: "your-domain-static-site-dev.example.com" for develop

### Upload config file for frontend app

#### Edit config file

#### Basic config

```bash
cd (project_root_dir/)frontend
cp src/config/config.json.sample src/config/config.json
vi src/config/config.json
```

#### AWS Cognito config (If use admin functions)

```bash
cp src/config/cognito-client-config.json.sample src/config/cognito-client-config.json
vi src/config/cognito-client-config.json
```

```json
{
  "Region": "ap-northeast-1",
  "UserPoolId": "ap-northeast-1_xxxxxxxxx",
  "ClientId": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "IdentityPoolId": "ap-northeast-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

#### Upload S3 Bucket "your-serverless-configs/your-project-name/frontend/{stage}"

#### Deploy continually on pushed to git

## Development

### Local Development

Install packages for development

```bash
cd (project_root/)serverless
. .venv/bin/activate
pip install pylint
```

### Work on local

Set venv

```bash
cd (project_root/)serverless
. .venv/bin/activate
```

Create Docker container only for the first time

```bash
cd (project_root/)serverless
docker-compose build
```

Start DynamoDB Local on Docker

```bash
cd (project_root)/serverless/develop/
docker-compose up -d
```

DynamomDB setup

```bash
cd (project_root/)serverless
sls dynamodb start
```

Execute below command

```bash
cd (project_root/)serverless
sls wsgi serve
```

Request [http://127.0.0.1:5000](http://127.0.0.1:5000/hoge)

If you want to stop DynamoDB Local on Docker

```bash
cd (project_root)/serverless/develop/
docker-compose stop
```

#### Execute Script

```bash
cd (project_root/)serverless
sls invoke local --function funcName --data param
```

### Convert existing DB records to DynamoDB

Install packages for converter if use MySQL for convert target service

```bash
cd (project_root/)serverless
. .venv/bin/activate
pip install PyMySQL
```

Set converter of target service

```bash
cd (root/)serverless/develop/db_converter/services/
git clone {repository url of target service converter}
```

Execute converter

```bash
cd (root/)serverless/develop/db_converter
python main.py {service_name}
```

### Performance Test

#### Setup K6

Install for macOS

```bash
brew install k6
```

#### Execute

```bash
k6 run ./dev_tools/performance/vote.js --vus NN --duration MMs
```

## Destroy Resources

Destroy for serverless resources

```bash
cd (project_root/)serverless
sls remove --stage Target-stage
sls delete_domain --stage Target-stage
```

Removed files in S3 Buckets named "your-domain.example.com-cloudfront-logs" and "your-domain.example.com"

Destroy for static server resources by Terraform

```bash
cd (project_root/)terraform
terraform destroy -auto-approve -var-file=./terraform.tfvars
```
