# CCprompt

## Code Context Prompt

### The Problem

When working with AI prompts, it is often necessary to provide code context to the model to generate useful responses. This can be a time-consuming task, especially when working with large codebases.
CCprompt is a tool designed to extract code context for AI prompts based on provided function or class names. It supports both Python and JavaScript/TypeScript codebases.
Providing such context can help AI models generate more accurate and relevant responses.

## Features

- Supports Python and JavaScript/TypeScript languages.
- Extracts functions or classes and their inheritance chains.
- Configurable via a JSON configuration file or command-line arguments.
- Excludes virtual environment directories if needed.

## Installation

```bash
pip install ccprompt
```

## Usage

### first time usage

run `ccprompt` it will create a configuration file `ccprompt_config.json` in the current directory.
fill in the configuration file with the required information. Alternatively, you can pass the required information as command-line arguments.
`ccprompt --config CONFIG`. The configuration file should be in the following format:

```json
{
    "target_name": "class name or function name",
    "project_path": "/path/to/project",
    "venv_site_packages_path": "/path/to/venv/lib/python3.x/site-packages",
    "exclude_venv": false,
    "output_file": "extracted_code.txt",
    "language": "python"
}

```

then run `ccprompt`, it will extract the code context based on the configuration file. and create `extracted_code.txt` that include extracted code context.

the extracted code will include file path, functions or classes and their inheritance chains.

Star and share the repository if you find it useful.

```bash
ccprompt --help
```

## Development

git clone the repository and navigate to the root directory.

### Install the Package

Navigate to the root directory where `setup.py` is located and run:

```bash
pip install .
