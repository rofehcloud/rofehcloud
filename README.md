# RofehCloud

Welcome to the RofehCloud project! This README will guide you through the setup and usage of the project.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Authors](#authors)
- [License](#license)

## Introduction

RofehCloud software is designed to help you with troubleshooting of simple and complex issues with Kubernetes and public clouds like AWS, Google Cloud (GCP), and Azure. 

The name RofehCloud is a play on Hebrew word "rofeh" that means "doctor".

## Features

- RofehCloud runs locally on your computer and for troubleshooting uses already configured cloud access credentials for CLI tools like "aws", "gcloud", "az" and "kubectl"
- The text-based tool provides an easy-to-use chat interface
- Supports OpenAI and AWS Bedrock Anthropic LLMs
- Protects from incidental change of data locally or in connected clouds

## Installation

To get started with RofehCloud, follow these steps (macOs environment):

1. Clone the repository:
    ```bash
    git clone https://github.com/rofehcloud/rofehcloud.git
    ```
2. Navigate to the project directory:
    ```bash
    cd rofehcloud
    ```
3. Create Python venv, activate it and install necessary dependencies:
    ```bash
    make venv
    source .venv/bin/activate
    make install
    ```
4. Review [config.py](common/config.py) for supported environment variables and their default values. Use the local `.env` local file to set any custom values.

## Usage

To start using RofehCloud, run the following command:
```bash
make run
```

This will launch the application in the terminal console.

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