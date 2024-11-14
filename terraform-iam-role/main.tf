variable "prj_prefix" {}
variable "region_default" {}
variable "aws_account_id" {}
variable "deployment_bucket_name" {}
variable "route53_zone_id" {}
variable "target_role_name" {}
variable "domain_static_site" {}
variable "domain_media_site" {}

resource "aws_iam_policy" "terraform_deploy_config" {
  name_prefix = join("-", ["terraform_deploy_config", var.prj_prefix])
  path        = "/"
  description = "IAM Policy for Terraform deployment configuration."

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "TerraformDeployConfigPolicy",
        "Effect" : "Allow",
        "Action" : [
          #"s3:ListBucket",
          #"s3:ListObjects",
          #"s3:GetObject",
          #"s3:PutObject",
          #"s3:DeleteObject",
          #"s3:GetBucketVersioning"
          "s3:*"
        ],
        "Resource" : [
          "arn:aws:s3:::${var.deployment_bucket_name}",
          "arn:aws:s3:::${var.deployment_bucket_name}/*"
          #"arn:aws:s3:::${var.deployment_bucket_name}/terraform/${var.prj_prefix}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "terraform_deploy_for_sls_base" {
  name_prefix = join("-", ["terraform_deploy_for_sls_base", var.prj_prefix])
  path        = "/"
  description = "IAM Policy for Terraform deployment."

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "TerraformDeployForSlsBasePolicy1",
        "Effect" : "Allow",
        "Action" : [
          "cloudfront:CreateCloudFrontOriginAccessIdentity",
          "cloudfront:CreateDistribution",
          "cloudfront:DeleteCloudFrontOriginAccessIdentity",
          "cloudfront:DeleteDistribution",
          "cloudfront:GetCloudFrontOriginAccessIdentity",
          "cloudfront:GetDistribution",
          "cloudfront:ListCachePolicies",
          "cloudfront:ListTagsForResource",
          "cloudfront:UpdateDistribution",
          "cloudfront:TagResource",
        ],
        "Resource" : [
          "arn:aws:cloudfront:*:${var.aws_account_id}:*"
        ]
      },
      {
        "Sid" : "TerraformDeployForSlsBasePolicy2",
        "Effect" : "Allow",
        "Action" : [
          "cloudfront:GetCachePolicy"
        ],
        "Resource" : [
          "arn:aws:cloudfront:*:${var.aws_account_id}:cache-policy/*"
        ]
      },
      {
        "Sid" : "TerraformDeployForSlsBasePolicy3",
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:CreateTable",
          "dynamodb:DeleteItem",
          "dynamodb:DeleteTable",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:DescribeContributorInsights",
          "dynamodb:DescribeExport",
          "dynamodb:DescribeGlobalTable",
          "dynamodb:DescribeGlobalTableSettings",
          "dynamodb:DescribeKinesisStreamingDestination",
          "dynamodb:DescribeLimits",
          "dynamodb:DescribeReservedCapacity",
          "dynamodb:DescribeReservedCapacityOfferings",
          "dynamodb:DescribeStream",
          "dynamodb:DescribeTable",
          "dynamodb:DescribeTableReplicaAutoScaling",
          "dynamodb:DescribeTimeToLive",
          "dynamodb:GetItem",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:ListBackups",
          "dynamodb:ListContributorInsights",
          "dynamodb:ListExports",
          "dynamodb:ListGlobalTables",
          "dynamodb:ListStreams",
          "dynamodb:ListTables",
          "dynamodb:ListTagsOfResource",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:RestoreTableFromBackup",
          "dynamodb:RestoreTableToPointInTime",
          "dynamodb:Scan",
          "dynamodb:TagResource",
          "dynamodb:UntagResource",
          "dynamodb:UpdateContinuousBackups",
          "dynamodb:UpdateContributorInsights",
          "dynamodb:UpdateGlobalTable",
          "dynamodb:UpdateGlobalTableSettings",
          "dynamodb:UpdateItem",
          "dynamodb:UpdateTable",
          "dynamodb:UpdateTableReplicaAutoScaling",
          "dynamodb:UpdateTimeToLive"
        ],
        "Resource" : [
          "arn:aws:dynamodb:${var.region_default}:${var.aws_account_id}:table/*"
          #"arn:aws:dynamodb:${var.region_default}:${var.aws_account_id}:table/${var.prj_prefix}-*"
        ]
      },
      {
        "Sid" : "TerraformDeployForSlsBasePolicy4",
        "Effect" : "Allow",
        "Action" : "iam:GetPolicyVersion",
        "Resource" : "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
      },
      {
        "Sid" : "TerraformDeployForSlsBasePolicy6",
        "Effect" : "Allow",
        "Action" : [
          "iam:AttachRolePolicy",
          "iam:CreateRole",
          "iam:CreateUser",
          "iam:DeleteRole",
          "iam:DeleteRolePolicy",
          "iam:DetachRolePolicy",
          "iam:GetPolicy",
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole",
          "iam:ListPolicies",
          "iam:ListRolePolicies",
          "iam:ListRoles",
          "iam:PutRolePolicy",
          "iam:UpdateRole",
          "iam:PassRole",
        ],
        "Resource" : [
          "arn:aws:iam::${var.aws_account_id}:*"
        ]
      },
      {
        "Sid" : "TerraformDeployForSlsBasePolicy7",
        "Effect" : "Allow",
        "Action" : [
          "route53:ChangeResourceRecordSets",
          "route53:GetHostedZone",
          "route53:ListResourceRecordSets"
        ],
        "Resource" : [
          "arn:aws:route53:::hostedzone/${var.route53_zone_id}"
        ]
      },
      {
        "Sid" : "TerraformDeployForSlsBasePolicy8",
        "Effect" : "Allow",
        "Action" : "s3:*",
        "Resource" : [
          "arn:aws:s3:::${var.domain_static_site}",
          "arn:aws:s3:::${var.domain_static_site}/*",
          "arn:aws:s3:::${var.domain_media_site}",
          "arn:aws:s3:::${var.domain_media_site}/*"
        ]
      },
      #{
      #  "Sid" : "TerraformDeployForSlsBasePolicy9",
      #  "Effect" : "Allow",
      #  "Action" : [
      #    "s3:GetObject",
      #    "s3:GetObjectAcl",
      #    "s3:PutObject",
      #    "s3:DeleteObject"
      #  ],
      #  "Resource" : [
      #    "arn:aws:s3:::${var.domain_static_site}/*",
      #    "arn:aws:s3:::${var.domain_media_site}/*"
      #  ]
      #},
      {
        "Sid" : "TerraformDeployForSlsBasePolicy10",
        "Effect" : "Allow",
        "Action" : [
          "acm:ListCertificates",
          "acm:RequestCertificate",
          "acm:AddTagsToCertificate",
          "acm:ListTagsForCertificate",
          "acm:DescribeCertificate",
          "acm:RemoveTagsFromCertificate",
          "acm:DeleteCertificate",
          "route53:ListHostedZones",
          "route53:GetChange",
          "iam:GetPolicy",
          "s3:ListBucket",
          "dynamodb:ListTables"
        ],
        "Resource" : [
          "*"
        ]
      }
    ]
  })
}

#resource "aws_iam_policy" "terraform_deploy_for_aurora_db" {
#  name_prefix = join("-", ["terraform_deploy_for_aurora_db", var.prj_prefix])
#  path        = "/"
#  description = "IAM Policy for Terraform deployment."
#
#  policy = jsonencode({
#    "Version" : "2012-10-17",
#    "Statement" : [
#      {
#        "Sid" : "TerraformDeployForAuroraDbPolicyEC2Main",
#        "Effect" : "Allow",
#        "Action" : [
#          "ec2:AssociateRouteTable",
#          "ec2:AttachInternetGateway",
#          "ec2:AuthorizeSecurityGroupEgress",
#          "ec2:AuthorizeSecurityGroupIngress",
#          "ec2:CreateInternetGateway",
#          "ec2:CreateRoute",
#          "ec2:CreateRouteTable",
#          "ec2:CreateSecurityGroup",
#          "ec2:CreateSubnet",
#          "ec2:CreateTags",
#          "ec2:CreateVPC",
#          "ec2:ModifyVpcAttribute",
#          "ec2:ModifySubnetAttribute",
#          "ec2:DeleteInternetGateway",
#          "ec2:DeleteRouteTable",
#          "ec2:DeleteSecurityGroup",
#          "ec2:DeleteSubnet",
#          "ec2:DeleteTags",
#          "ec2:DeleteVPC",
#          "ec2:DetachInternetGateway",
#          "ec2:DisassociateRouteTable",
#          "ec2:ModifyInstanceAttribute",
#          "ec2:RevokeSecurityGroupEgress",
#          "ec2:RevokeSecurityGroupIngress",
#          "ec2:StartInstances",
#          "ec2:StopInstances",
#          "ec2:TerminateInstances"
#        ],
#        "Resource" : [
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:*"
#        ]
#      },
#      {
#        "Sid" : "TerraformDeployForAuroraDbPolicyEC2Run",
#        "Effect" : "Allow",
#        "Action" : [
#          "ec2:RunInstances",
#        ],
#        "Resource" : [
#          "arn:aws:ec2:${var.region_default}::image/*",
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:instance/*",
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:key-pair/*",
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:security-group/*",
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:network-interface/*",
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:subnet/*",
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:volume/*",
#          "arn:aws:ec2:${var.region_default}:${var.aws_account_id}:vpc/*"
#        ]
#      },
#      {
#        "Sid" : "TerraformDeployForAuroraDbPolicyRDSMain",
#        "Effect" : "Allow",
#        "Action" : [
#          "rds:CreateDBInstance",
#          "rds:CreateDBParameterGroup",
#          "rds:DeleteDBInstance",
#          "rds:DeleteDBParameterGroup",
#          "rds:DeleteDBSubnetGroup",
#          "rds:ModifyDBInstance",
#          "rds:ModifyDBParameterGroup",
#          "rds:RemoveTagsFromResource",
#          "rds:CreateDBCluster",
#          "rds:DeleteDBCluster",
#          "rds:ModifyDBCluster",
#          "rds:CreateDBClusterParameterGroup",
#          "rds:DeleteDBClusterParameterGroup",
#          "rds:ModifyDBClusterParameterGroup",
#          "rds:RegisterDBProxyTargets",
#          "rds:DeregisterDBProxyTargets",
#          "rds:DeleteDBSubnetGroup"
#        ],
#        "Resource" : [
#          "arn:aws:rds:${var.region_default}:${var.aws_account_id}:*:${var.prj_prefix}-*",
#          "arn:aws:rds:${var.region_default}:${var.aws_account_id}:subgrp:*"
#        ]
#      },
#      {
#        "Sid" : "TerraformDeployForAuroraDbPolicyRDSTags",
#        "Effect" : "Allow",
#        "Action" : [
#          "rds:AddTagsToResource",
#        ],
#        "Resource" : [
#          "arn:aws:rds:${var.region_default}:${var.aws_account_id}:*"
#        ]
#      },
#      {
#        "Sid" : "TerraformDeployForAuroraDbPolicyRDSDiscribe",
#        "Effect" : "Allow",
#        "Action" : [
#          "rds:DescribeDBClusterParameterGroups",
#          "rds:DescribeDBClusterParameters",
#          "rds:DescribeDBClusters",
#          "rds:DescribeDBInstances",
#          "rds:DescribeDBParameterGroups",
#          "rds:DescribeDBParameters",
#          "rds:DescribeDBSubnetGroups",
#          "rds:DescribeGlobalClusters",
#          "rds:ListTagsForResource",
#        ],
#        "Resource" : "*"
#      },
#      {
#        "Sid" : "TerraformDeployForAuroraDbPolicy3",
#        "Effect" : "Allow",
#        "Action" : [
#          "secretsmanager:CreateSecret",
#          "secretsmanager:DeleteSecret",
#          "secretsmanager:DescribeSecret",
#          "secretsmanager:GetResourcePolicy",
#          "secretsmanager:GetSecretValue",
#          "secretsmanager:PutSecretValue"
#        ],
#        "Resource" : [
#          "arn:aws:secretsmanager:${var.region_default}:${var.aws_account_id}:*"
#        ]
#      },
#      {
#        "Sid" : "TerraformDeployForDbProxy",
#        "Effect" : "Allow",
#        "Action" : [
#          "rds:CreateDBProxy",
#          "rds:DeleteDBProxy",
#          "rds:ModifyDBProxy",
#          "rds:RegisterDBProxyTargets",
#          "rds:DeregisterDBProxyTargets",
#          "rds:ModifyDBProxyTargetGroup",
#          "rds:DescribeDBProxyTargetGroups",
#          "rds:DescribeDBProxies",
#          "rds:CreateDBProxyEndpoint",
#          "rds:DeleteDBProxyEndpoint",
#          "rds:ModifyDBProxyEndpoint",
#          "rds:DescribeDBProxyEndpoints",
#          "rds:DescribeDBProxyTargets",
#        ],
#        "Resource" : [
#          "arn:aws:rds:${var.region_default}:${var.aws_account_id}:db-proxy:*",
#          "arn:aws:rds:${var.region_default}:${var.aws_account_id}:db-proxy-endpoint:*",
#          "arn:aws:rds:${var.region_default}:${var.aws_account_id}:target-group:*"
#        ]
#      },
#      {
#        "Sid" : "TerraformDeployForAuroraDbPolicy5",
#        "Effect" : "Allow",
#        "Action" : [
#          "route53:ListHostedZones",
#          "ec2:DescribeImages",
#          "ec2:DescribeVpcs",
#          "ec2:DescribeVpcClassicLink",
#          "ec2:DescribeVpcClassicLinkDnsSupport",
#          "ec2:DescribeSecurityGroups",
#          "ec2:DescribeAccountAttributes",
#          "ec2:DescribeInstanceAttribute",
#          "ec2:DescribeInstanceCreditSpecifications",
#          "ec2:DescribeInstanceTypes",
#          "ec2:DescribeInstances",
#          "ec2:DescribeInternetGateways",
#          "ec2:CreateNetworkInterface",
#          "ec2:DescribeNetworkInterfaces",
#          "ec2:DeleteNetworkInterface",
#          "ec2:DescribeRouteTables",
#          "ec2:DescribeSecurityGroups",
#          "ec2:DescribeSubnets",
#          "ec2:DescribeTags",
#          "ec2:DescribeVolumes",
#          "ec2:DescribeVpcAttribute",
#          "ec2:DescribeIamInstanceProfileAssociations",
#          "rds:CreateDBSubnetGroup"
#        ],
#        "Resource" : [
#          "*"
#        ]
#      },
#    ]
#  })
#}

resource "aws_iam_policy" "serverless_deploy" {
  name_prefix = join("-", ["serverless_deploy", var.prj_prefix])
  path        = "/"
  description = "IAM Policy for Serverless deployment."

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      #{
      #  "Sid" : "ServerlessDeployConfigPolicy",
      #  "Effect" : "Allow",
      #  "Action" : [
      #    "s3:CreateBucket",
      #    "s3:DeleteBucket",
      #    "s3:ListAllMyBuckets",
      #    "s3:ListBucket",
      #    "s3:ListBuckets",
      #    "s3:ListBucketVersions",
      #  ],
      #  "Resource" : [
      #    "arn:aws:s3:::*"
      #  ]
      #},
      #{
      #  "Sid" : "ServerlessDeployPolicy10",
      #  "Effect" : "Allow",
      #  "Action" : [
      #    "lambda:AddPermission",
      #    "lambda:CreateAlias",
      #    "lambda:CreateEventSourceMapping",
      #    "lambda:CreateFunction",
      #    "lambda:DeleteAlias",
      #    "lambda:DeleteEventSourceMapping",
      #    "lambda:DeleteFunction",
      #    "lambda:Get*",
      #    "lambda:InvokeFunction",
      #    "lambda:List*",
      #    "lambda:PublishVersion",
      #    "lambda:RemovePermission",
      #    "lambda:TagResource",
      #    "lambda:UntagResource",
      #    "lambda:UpdateFunctionCode",
      #    "lambda:Update*",
      #  ],
      #  "Resource" : [
      #    "arn:aws:lambda:${var.region_default}:${var.aws_account_id}:function:${var.prj_prefix}-*"
      #  ]
      #},
      {
        "Sid" : "ServerlessDeployPolicyLambdaLayer",
        "Effect" : "Allow",
        "Action" : [
          "lambda:*",
          #"lambda:PublishLayerVersion",
          #"lambda:GetLayerVersion",
          #"lambda:DeleteLayerVersion"
        ],
        "Resource" : "*"
        #"Resource" : [
        #  "arn:aws:lambda:${var.region_default}:*",
        #  #"arn:aws:lambda:${var.region_default}:${var.aws_account_id}:function:*"
        #  #"arn:aws:lambda:${var.region_default}:${var.aws_account_id}:layer:*",
        #  #"arn:aws:lambda:${var.region_default}:${var.aws_account_id}:layer:${var.prj_prefix}-*"
        #]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "apigateway:GET",
          "apigateway:POST",
          "apigateway:PUT",
          "apigateway:DELETE",
          "apigateway:PATCH"
        ],
        "Resource" : "arn:aws:apigateway:${var.region_default}::/*",
        #"Resource" : [
        #  "arn:aws:apigateway:${var.region_default}::/restapis/*",
        #  "arn:aws:apigateway:${var.region_default}::/domainnames",
        #  "arn:aws:apigateway:${var.region_default}::/domainnames/*",
        #  "arn:aws:apigateway:${var.region_default}::/tags/*"
        #]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "cloudformation:CancelUpdateStack",
          "cloudformation:ContinueUpdateRollback",
          "cloudformation:CreateStack",
          "cloudformation:DeleteStack",
          "cloudformation:DeleteStackSet",
          "cloudformation:DescribeChangeSet",
          "cloudformation:DescribeStackEvents",
          "cloudformation:DescribeStackSetOperation",
          "cloudformation:DescribeStackResource*",
          "cloudformation:DescribeStacks",
          "cloudformation:ExecuteChangeSet",
          "cloudformation:GetStackPolicy",
          "cloudformation:GetTemplate",
          "cloudformation:ListChangeSets",
          "cloudformation:ListStacks",
          "cloudformation:ListStackResources",
          "cloudformation:UpdateStack",
          "cloudformation:UpdateStackSet",
          "cloudformation:CreateChangeSet",
          "cloudformation:DeleteChangeSet",
          "cloudformation:UpdateTerminationProtection",
          "cloudformation:SetStackPolicy",
        ],
        "Resource" : "*"
        #"Resource" : "arn:aws:cloudformation:${var.region_default}:${var.aws_account_id}:*/${var.prj_prefix}/*"
        #"Resource" : "arn:aws:cloudformation:${var.region_default}:${var.aws_account_id}:stack/${var.prj_prefix}/*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "cloudformation:ValidateTemplate",
          "cloudformation:GetTemplate",
          "cloudformation:GetTemplateSummary",
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "cloudwatch:DescribeAlarms",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:DeleteAlarms",
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:SetAlarmState",
        ],
        "Resource" : [
          "arn:aws:cloudwatch:${var.region_default}:${var.aws_account_id}:alarm:*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "cloudwatch:PutDashboard",
          "cloudwatch:GetDashboard",
          "cloudwatch:DeleteDashboard",
          "cloudwatch:ListDashboards"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DeleteLogGroup",
          "logs:DeleteLogStream",
          "logs:DeleteRetentionPolicy",
          "logs:DeleteSubscriptionFilter",
          "logs:GetLogEvents",
          "logs:PutMetricFilter",
          "logs:PutLogEvents",
          "logs:PutRetentionPolicy",
          "logs:PutSubscriptionFilter",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:TagResource"
        ],
        "Resource" : [
          "arn:aws:logs:${var.region_default}:${var.aws_account_id}:log-group:*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ec2:DescribeVpcEndpoints",
          "ec2:CreateVpcEndpoint",
          "ec2:DeleteVpcEndpoints"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "events:Describe*",
          "events:Get*",
          "events:List*",
          "events:CreateEventBus",
          "events:DeleteEventBus",
          "events:PutRule",
          "events:DeleteRule",
          "events:PutTargets",
          "events:RemoveTargets",
          "events:TagResource",
          "events:UntagResource"
        ],
        "Resource" : [
          "arn:aws:events:${var.region_default}:${var.aws_account_id}:event-bus/*",
          "arn:aws:events:${var.region_default}:${var.aws_account_id}:rule/*",
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "wafv2:*",
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_policy" "cognito_deploy" {
  name_prefix = join("-", ["cognito_deploy", var.prj_prefix])
  path        = "/"
  description = "IAM Policy for Cognito deployment."

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      #{
      #  "Effect" : "Allow",
      #  "Action" : [
      #    "cognito-idp:CreateUserPool",
      #    "cognito-idp:UpdateUserPool",
      #    "cognito-idp:DeleteUserPool",
      #    "cognito-idp:DescribeUserPool",
      #    "cognito-idp:GetUserPoolMfaConfig",
      #    "cognito-idp:TagResource",
      #    "cognito-idp:CreateUserPoolClient",
      #    "cognito-idp:UpdateUserPoolClient",
      #    "cognito-idp:DeleteUserPoolClient",
      #    "cognito-identity:CreateIdentityPool",
      #    "cognito-identity:UpdateIdentityPool",
      #    "cognito-identity:DeleteIdentityPool",
      #  ],
      #  "Resource" : "*"
      #  #"Resource" : [
      #  #  "arn:aws:cognito-idp:${var.region_default}:${var.aws_account_id}:userpool/*",
      #  #  "arn:aws:cognito-identity:${var.region_default}:${var.aws_account_id}:identitypool/*"
      #  #]
      #},
      {
        "Sid" : "VisualEditor2",
        "Effect" : "Allow",
        "Action" : [
          "cognito-identity:CreateIdentityPool",
          "cognito-identity:DeleteIdentityPool",
          "cognito-identity:DescribeIdentityPool",
          "cognito-identity:TagResource",
          "cognito-identity:UntagResource",
          "cognito-identity:UpdateIdentityPool"
        ],
        "Resource" : [
          "arn:aws:cognito-identity:${var.region_default}:${var.aws_account_id}:*"
        ]
      },
      {
        "Sid" : "VisualEditor3",
        "Effect" : "Allow",
        "Action" : [
          "cognito-idp:AddCustomAttributes",
          "cognito-idp:CreateUserPool",
          "cognito-idp:CreateUserPoolClient",
          "cognito-idp:DeleteUserPool",
          "cognito-idp:DeleteUserPoolClient",
          "cognito-idp:DescribeUserPool",
          "cognito-idp:DescribeUserPoolClient",
          "cognito-idp:GetUserPoolMfaConfig",
          "cognito-idp:TagResource",
          "cognito-idp:UntagResource",
          "cognito-idp:UpdateUserPool",
          "cognito-idp:AdminCreateUser",
          "cognito-idp:AdminSetUserPassword"
        ],
        "Resource" : [
          "arn:aws:cognito-idp:${var.region_default}:${var.aws_account_id}:*"
        ]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "terraform_deploy_config_attachment" {
  role       = var.target_role_name
  policy_arn = aws_iam_policy.terraform_deploy_config.arn
}

resource "aws_iam_role_policy_attachment" "terraform_deploy_for_sls_base_attachment" {
  role       = var.target_role_name
  policy_arn = aws_iam_policy.terraform_deploy_for_sls_base.arn
}

#resource "aws_iam_role_policy_attachment" "terraform_deploy_for_aurora_db_attachment" {
#  role       = var.target_role_name
#  policy_arn = aws_iam_policy.terraform_deploy_for_aurora_db.arn
#}

resource "aws_iam_role_policy_attachment" "serverless_deploy_attachment" {
  role       = var.target_role_name
  policy_arn = aws_iam_policy.serverless_deploy.arn
}

resource "aws_iam_role_policy_attachment" "cognito_deploy_attachment" {
  role       = var.target_role_name
  policy_arn = aws_iam_policy.cognito_deploy.arn
}
