# Demo genai-codechecker

A tool that uses generative AI to automatically fix linting issues in your code.

## AWS Integration

This tool leverages AWS Bedrock, a fully managed service that offers access to high-performing foundation models for generative AI. You can select from various language models including:

- Anthropic Claude (Claude 3 Haiku, Sonnet)
- Amazon Titan
- Meta Llama 2
- And more

### Configuration

The tool requires proper AWS credentials and permissions to access Amazon Bedrock. Ensure you have:

1. AWS CLI configured with appropriate credentials
2. IAM permissions to access Amazon Bedrock
3. Access enabled for your chosen foundation model in AWS Bedrock

### Cost Awareness

**Important:** Using this tool incurs AWS charges based on:
- The selected foundation model
- Number of input tokens processed
- Number of output tokens generated
- API calls made to AWS Bedrock

Please refer to AWS services pricing page for detailed pricing information.

### Model Selection

You can configure your preferred model in `config.ini`:

```ini
[Bedrock]
region=us-east-1
model_id=anthropic.claude-3-haiku-20240307-v1:0
tuning_args={
    "max_tokens": 20000,
    "temperature": 1,
    "top_p": 0.999
}
```

## Overview

genai-codechecker analyzes your codebase for linting errors and uses AI to suggest and apply fixes automatically. It helps maintain consistent code quality and style across your projects.

## Features

- Automatic detection of linting issues
- AI-powered fix suggestions
- Batch processing of multiple files
- Support for popular linting tools
- Easy integration with existing workflows

## Usage

It works only with PMD for this demo [https://pmd.github.io/](https://pmd.github.io/).

## Installation

You need to install PMD somewhere on your machine after downloading it.

Update the file config.ini with your values : 

```ini
[Tools]
pmd.cmd=./tools/pmd-bin-7.9.0/bin/pmd check -d {input_file} -f json --rulesets=https://raw.githubusercontent.com/pmd/pmd/refs/heads/main/pmd-core/src/main/resources/rulesets/internal/all-java.xml -r violations.json
```

Create a python environment with the command : 

```bash
python3 -m venv .venv
```

Enable your python environment : 

```bash
source .venv/bin/activate
```

Install the dependencies : 

```bash
pip install -r requirements.txt
```

Configure if necessary our AWS credentials : 

```bash
aws configure
```

Choose a model ID from your AWS Account on [Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html).

Update the config.ini with our model configuration  

```ini

[Bedrock]
region=us-east-1
model_id = us.anthropic.claude-3-5-haiku-20241022-v1:0
tuning_args={  "anthropic_version": "bedrock-2023-05-31", "max_tokens": 20000, "top_k": 250,    "temperature": 1,    "top_p": 0.999}

```

## Execution

To launch the demo the command line is : 

```bash
python script.py SourceFile.java
```

The script will generate a new file with the extension "fixed" including the corrections provided by our model.


