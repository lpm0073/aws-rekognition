#------------------------------------------------------------------------------
# written by: Lawrence McDaniel
#             https://lawrencemcdaniel.com/
#
# date:       sep-2023
#
# usage:      all computed out values
#------------------------------------------------------------------------------
output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}
output "aws_region" {
  value = var.aws_region
}
output "aws_profile" {
  value = var.aws_profile
}

output "stage" {
  value = var.stage
}
output "api_gateway_arn" {
  value = aws_api_gateway_deployment.facialrecognition.id
}

output "api_gateway_url" {
  value = "https://${aws_route53_record.api.fqdn}"
}

output "lambda_index" {
  value = aws_lambda_function.index_function.arn
}

output "lambda_search" {
  value = aws_lambda_function.search_function.arn
}

output "s3_bucket" {
  value = module.s3_bucket.s3_bucket_bucket_domain_name
}

output "dynamodb_table" {
  value = module.dynamodb_table.dynamodb_table_arn
}

output "aws_api_gateway_api_key" {
  value     = aws_api_gateway_api_key.facialrecognition.value
  sensitive = true
}
