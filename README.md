---
title: Amazon Review Framework
emoji: 📝
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 5.23.1
app_file: app.py
pinned: false
---

# Amazon Review Framework API

A comprehensive system for creating Exceptional product reviews to qualify for the Amazon Vine program.

## Overview

This API provides access to the Amazon Review Framework, a structured system designed to help reviewers create high-quality, engaging product reviews. The framework consists of multiple JSON components that work together to guide the review process from information gathering to final polish.

The platform includes both a REST API and an interactive Gradio interface that uses Anthropic's Claude model to generate reviews based on user input and the framework components.

## Framework Components

The framework consists of the following key components:

- **framework-config.json**: Core configuration and workflow
- **review-strategy.json**: Strategic goals and principles
- **question-framework.json**: Strategic questioning methodology
- **product-analysis.json**: Product testing frameworks
- **image-analysis.json**: Image assessment guidelines
- **content-structure.json**: Section organization templates
- **keyword-strategy.json**: Search optimization approach
- **writing-process.json**: Content creation workflow
- **personality-balance.json**: Information/personality ratios
- **personality-techniques.json**: Humor & creative techniques
- **thematic-frameworks.json**: Theme development frameworks
- **narrative-sensory.json**: Storytelling & sensory frameworks
- **quality-assessment.json**: Quality evaluation criteria
- **redundancy-verification.json**: Duplication prevention
- **examples-templates.json**: Implementation examples

## API Endpoints

- `GET /`: HTML landing page with framework overview
- `GET /files`: List all available framework files
- `GET /files/{filename}`: Get a specific framework file
- `GET /framework`: Get complete framework data
- `POST /generate-review`: Generate a review using Claude and the framework
- `GET /gradio`: Interactive Gradio interface for generating reviews
- `GET /docs`: Interactive API documentation (Swagger UI)
- `GET /redoc`: Alternative API documentation (ReDoc)

## Usage Examples

### List all framework files

```bash
curl -X GET https://your-space-name.hf.space/files
```

### Get a specific framework file

```bash
curl -X GET https://your-space-name.hf.space/files/framework-config.json
```

### Get the complete framework

```bash
curl -X GET https://your-space-name.hf.space/framework
```

### Generate a review using Claude

```bash
curl -X POST https://your-space-name.hf.space/generate-review \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Glass Measuring Cup Set",
    "product_category": "Kitchen",
    "user_experience": "I bought these glass measuring cups last month. They\'re perfect for measuring small amounts for coffee brewing. One broke when I dropped it on my hardwood floor, but the other has been very durable.",
    "include_components": ["content-structure.json", "personality-balance.json"]
  }'
```

### Interactive Interface

For an interactive experience, visit the Gradio interface at:
```
https://your-space-name.hf.space/gradio
```

## Implementation Notes

This API is implemented using FastAPI and hosted on Hugging Face Spaces. The framework files are stored as JSON in the `/framework` directory and served through a simple REST API.

## Local Development

To run this API locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the setup script: `bash setup.sh`
4. Start the server: `uvicorn app:app --reload`

The API will be available at http://localhost:8000

## License

This framework is provided for educational and personal use.