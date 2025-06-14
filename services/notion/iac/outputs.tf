# Outputs for the Notion Webhook Lambda infrastructure

output "webhook_url" {
  description = "The webhook URL to use in Notion"
  value       = aws_lambda_function_url.webhook_url.function_url
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.webhook_handler.function_name
}

output "github_pat_parameter_name" {
  description = "SSM Parameter name for GitHub PAT"
  value       = aws_ssm_parameter.github_pat.name
}
