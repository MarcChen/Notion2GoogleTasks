# Variables for Notion Webhook Lambda Function

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "notion2googletasks"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "github_repo_owner" {
  description = "GitHub repository owner"
  type        = string
}

variable "github_repo_name" {
  description = "GitHub repository name"
  type        = string
  default     = "Notion2GoogleTasks"
}

variable "github_pat" {
  description = "GitHub Personal Access Token for triggering workflows"
  type        = string
  sensitive   = true
}

variable "notion_verification_token" {
  description = "Notion webhook verification token for signature verification"
  type        = string
  sensitive   = true
}

# New variables needed for webhook_handler.py
variable "github_workflow_file" {
  description = "GitHub workflow file name to trigger"
  type        = string
  default     = "sync_notion_page_webhook.yml"
}

variable "github_target_branch" {
  description = "GitHub target branch for workflow dispatch"
  type        = string
  default     = "main"
}