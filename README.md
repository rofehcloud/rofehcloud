# RofehCloud

Welcome to the RofehCloud project! This README will guide you through the setup and usage of the project.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)

## Introduction

RofehCloud software is designed to help you with troubleshooting of simple and complex issues with Kubernetes and public clouds like AWS, Google Cloud (GCP), and Azure. 

Ideal users of RofehCloud are:
- Cloud/support engineers working for an MSP supporting many customers with widely different cloud/K8s environments
- Production DevOps/SRE engineers interested in shorten their SaaS troubleshooting times
- Software development engineers working with development/staging environments and interested be more effective in operating and troubleshooting the environments


The name RofehCloud is a play on Hebrew word "rofeh" that means "doctor".

## Features

- RofehCloud runs locally on your computer and for troubleshooting uses your already configured cloud access credentials for CLI tools like "aws", "gcloud", "az" and "kubectl"
- The text-based tool provides an easy-to-use chat interface
- Supports OpenAI and AWS Bedrock Anthropic Claude LLMs
- Protects from incidental change of data locally or in connected clouds

RofehCloud does not require any additional components to be installed in the troubleshooted public cloud or K8s environments.

Some examples of queries/issues RofehCloud can handle:
- In what AWS regions do we have running EC2 instances?
- Do we have any unused EBS volumes?
- Why I cannot create S3 bucket named my_new_unique_s3_bucket_xcq?
- How to modify AWS policy xyz to allow write access to S3 bucket mybucket?
- Do we have any public S3 buckets?
- Why do we have two pending k8s pods? How to fix them?


## Installation

### Prerequisites
To successfully deploy and use RofehCloud you will need the following tools and resources:

Software:
- Python 3.10 or newer
- make
- git
- aws (needed if you use AWS)
- gcloud (needed if you use Google Cloud)
- az (needed if you use Azure)
- kubectl (needed if you use Kubernetes)

RofehCloud can work with one of the following LLM services:
- OpenAI Enterprise API (default LLM):
   - Configure the API key in environment variable OPENAI_API_KEY
   - Recommended (default) OpenAI models are gpt-4o and gpt-4o-mini
- Anthropic Claude models running on AWS Bedrock service:
   - Set environment variable LLM_TO_USE to "bedrock"
   - If the AWS Bedrock service is accessible using a non-default AWS profile, then set the profile name in environment variable BEDROCK_PROFILE_NAME and AWS Bedrock region code name (like "us-west-2") in variable BEDROCK_AWS_REGION
   - By default RofehCloud uses Anthropic models Claude 3.5 Sonnet and Claude 3 Haiku

To get started with RofehCloud, follow these steps (macOs environment):

1. Clone the repository:
    ```bash
    git clone https://github.com/rofehcloud/rofehcloud.git
    ```
2. Navigate to the project directory:
    ```bash
    cd rofehcloud
    ```
3. Create Python venv, activate it and install necessary Python dependencies:
    ```bash
    make venv
    source .venv/bin/activate
    make install
    ```
4. Review [config.py](common/config.py) for supported environment variables and their default values. Use the local `.env` local file to set any custom values.

An example of `.env` file format:
```
OPENAI_API_KEY=sk-xxx-xxxxxxxxxxxxxxxxxxxxxxxxxxx
BEDROCK_PROFILE_NAME=bedrock_profile
BEDROCK_AWS_REGION=us-east-2
LLM_TO_USE=openai
```

## Usage

To start using RofehCloud, run the following command:
```bash
make run
```

This will launch the application in the terminal console.

## FAQ

### How does RofehCloud prevent incidental modification of connected cloud resources?
By default, RofehCloud will validate every LLM-suggested CLI command whether the command can make any changes in the target system. If RofehCloud detects that the planned command can make a change, the tool will pause and ask for user confirmation whether to execute the command or not. For example:
```
? Enter your question:  Please create a new S3 bucket my-new-secret-bucket-for-test-data

New conversation label: Create S3 bucket for test data

> Entering new AgentExecutor chain...
To create an S3 bucket, I need to use the AWS CLI. I will proceed to run the command to create the bucket.

Action: Run a shell command or access CLI tools
Action Input: aws s3api create-bucket --bucket my-new-secret-bucket-for-test-data --region us-east-1

Attention! The system would like to execute a command that may change some data.
The command that is planned to be executed:
aws s3api create-bucket --bucket my-new-secret-bucket-for-test-data --region us-east-1

? Would you like the command to be executed? (Y/n)
```

### Is there a way for the user to review and approve every command executed by RofehCloud?
Yes, this is possible. To enable the feature please set environment variable `ASK_FOR_USER_CONFIRMATION_BEFORE_EXECUTING_EACH_COMMAND` to value `true`, either using `export` command or in local `.env` file. For example:
```bash
export ASK_FOR_USER_CONFIRMATION_BEFORE_EXECUTING_EACH_COMMAND=true
```

or in the local .env file:
```
ASK_FOR_USER_CONFIRMATION_BEFORE_EXECUTING_EACH_COMMAND=true
```

### Does RofehCloud support MinIO and OpenShift?
Yes, just add the names of relevant CLI tools to environment variable ADDITIONAL_TOOLS; for example:
```
export ADDITIONAL_TOOLS=mc,oc
```


## Contributing

We welcome contributions to the RofehCloud project! If you would like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push them to your fork.
4. Submit a pull request with a detailed description of your changes.

## Authors

The project was initially created by:
- **Victor Gartvich** - original developer
- **Andre Buryndin** - code reviews and contributions

## License

This project is licensed under the Mozilla Public License, version 2.0. See the [LICENSE.txt](LICENSE.txt) file for more details.

Thank you for using RofehCloud!