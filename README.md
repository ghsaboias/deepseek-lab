# Repository Structure Analyzer

A tool that analyzes GitHub repository structures and generates AI-powered summaries using Groq's API.

## Features

- 📂 Recursive repository structure analysis
- 🤖 AI-generated insights about project architecture
- 📝 Automatic summary generation in markdown format
- 💾 Cached structure storage in `repo_structure.txt`
- 🔍 File content analysis with smart truncation

## Goals

1. Provide quick understanding of complex codebases
2. Identify potential architectural improvements
3. Document repository structure automatically
4. Enable batch analysis of multiple files

## Setup

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Create `.env` file with:

```bash
GITHUB_OWNER="your_org"
GITHUB_REPO="repo_name"
GITHUB_TOKEN="ghp_..."
GROQ_API_KEY="gsk_..."
```

## Usage

```bash
python main.py
```

## Outputs

- `summary.txt`: AI-generated repository analysis
- `repo_structure.txt`: Cached structure tree 

## Example Structure

```
📁 Repository Structure
├── src/
│ ├── app/ # Next.js application
│ │ ├── api/ # Backend endpoints
│ │ └── pages/ # Frontend routes
│ └── services/ # Business logic
└── tests/ # Test suites
```

## Customization

Modify `main.py` to:
- Adjust batch sizes (`batch_size` in `summarize_repository`)
- Change AI model (`deepseek-r1-distill-llama-70b`)
- Enable/disable file content analysis
- Modify structure depth limits

> **Note** Requires GitHub repository read access and Groq API key

## License

This project is open-sourced under the MIT License - see the LICENSE file for details.
    