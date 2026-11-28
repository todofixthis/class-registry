# This repo's GitHub settings, provisioned by the todofixthis module
# (ADR 025 in todofixthis/cookiecutter-py). The values this project owns live
# in terraform.tfvars, which template updates leave alone.
terraform {
  required_version = ">= 1.9"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "github" {
  owner = "todofixthis"
}

variable "description" {
  description = "The repo's description on GitHub. A variable so this project can keep its own wording through template updates."
  type        = string
}

variable "homepage_url" {
  default     = null
  description = "Where the repo page links to, usually the project's docs. A variable so this project can point it elsewhere, or nowhere."
  type        = string
}

variable "topics" {
  default     = []
  description = "The repo's GitHub topics. A variable because each project chooses its own."
  type        = list(string)
}

module "repository" {
  source = "github.com/todofixthis/terraform-github-repository?ref=v1.1.0"

  description  = var.description
  homepage_url = var.homepage_url
  name         = "class-registry"
  topics       = var.topics
}
