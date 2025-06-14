# AWS Systems Manager Parameter Store resources

# GitHub Personal Access Token
resource "aws_ssm_parameter" "github_pat" {
  name        = "/${var.project_name}/${var.environment}/github/pat"
  description = "GitHub Personal Access Token for triggering workflows"
  type        = "SecureString"
  value       = var.github_pat

  tags = {
    Name        = "${var.project_name}-github-pat"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Notion Webhook Verification Token
resource "aws_ssm_parameter" "notion_verification_token" {
  name        = "/${var.project_name}/${var.environment}/notion/verification-token"
  description = "Notion webhook verification token for signature verification"
  type        = "SecureString"
  value       = var.notion_verification_token

  tags = {
    Name        = "${var.project_name}-notion-verification-token"
    Environment = var.environment
    Project     = var.project_name
  }
}
