# Overview

Welcome to the world of DevSecOps! You have heard of DevOps. Nowadays, DevSecOps is becoming more popular. How can Security organizations enable developers build security into their products and services? In this workshop, you will experience how tooling and automation can create a security conscious culture throughout the development lifecycle while scaling to the demands of the business.
We will see an example of how to stop code that erroneously contains stray AWS credentials (we revoked them first, of course) from being deployed.


* **Level**: Intermediate
* **Duration**: 2 hours
* **<a href="https://aws.amazon.com/blogs/security/new-whitepaper-now-available-the-security-perspective-of-the-aws-cloud-adoption-framework/" target="_blank">AWS CAF</a>**: Security Perspective
* **<a href="https://awssecworkshops.com/getting-started/" target="_blank">Prerequisites</a>**: AWS Account, Admin IAM User

## Scenario

For this workshop, you will build a pipeline using AWS CodePipeline and AWS Lambda.  Amazon S3 will be your code repository.  Your developers want to deploy an AWS Cloudformation template.  However, you need to ensure it is secure before it is released to production.


## Region
Please use the **us-west-2 (Oregon)** region for this workshop.

