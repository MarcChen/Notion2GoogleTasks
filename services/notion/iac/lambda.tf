# Lambda function and related resources

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "webhook_lambda_logs" {
  name              = "/aws/lambda/${var.project_name}-webhook-handler-${var.environment}"
  retention_in_days = 1

  tags = {
    Name        = "${var.project_name}-webhook-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda function
resource "aws_lambda_function" "webhook_handler" {
  filename         = "webhook_handler.zip"
  source_code_hash = filebase64sha256("webhook_handler.zip")
  function_name    = "${var.project_name}-webhook-handler-${var.environment}"
  role             = "arn:aws:iam::649938092864:role/Notion2GoogleTasks-webhook-lambda-role-prod"
  handler          = "webhook_handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 300
  memory_size      = 256

  environment {
    variables = {
      GITHUB_REPO_OWNER                   = var.github_repo_owner
      GITHUB_REPO_NAME                    = var.github_repo_name
      GITHUB_PAT_PARAMETER_NAME           = aws_ssm_parameter.github_pat.name
      NOTION_VERIFICATION_TOKEN_PARAMETER = aws_ssm_parameter.notion_verification_token.name
      PROJECT_NAME                        = var.project_name
      ENVIRONMENT                         = var.environment
      GITHUB_WORKFLOW_FILE                = var.github_workflow_file
      GITHUB_TARGET_BRANCH                = var.github_target_branch
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.webhook_lambda_logs,
  ]

  tags = {
    Name        = "${var.project_name}-webhook-handler"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda Function URL (replaces API Gateway)
resource "aws_lambda_function_url" "webhook_url" {
  function_name      = aws_lambda_function.webhook_handler.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_methods     = ["POST"]
    allow_origins     = ["*"]
    allow_headers     = ["date", "keep-alive", "content-type", "x-notion-signature"]
    expose_headers    = ["date", "keep-alive"]
    max_age           = 86400
  }
}
