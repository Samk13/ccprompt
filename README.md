# CCprompt

## Code Context Prompt

### The Problem

When working with AI prompts, it is often necessary to provide code context to the model to generate useful responses. This can be a time-consuming task, especially when working with large codebases.
CCprompt is a tool designed to extract code context for AI prompts based on provided function or class names. It supports both Python codebases.
Providing such context can help AI models generate more accurate and relevant responses.

## Features

- Supports Python codebase.
- Extracts functions or classes and their inheritance chains
- Configurable via a JSON configuration file or command-line arguments
- Excludes virtual environment directories if needed
- Zero runtime dependencies for Python-only usage
- Optional JavaScript support via esprima

## Installation

### Using uv (recommended)

```bash
uv add ccprompt
```

### Using pip

```bash
pip install ccprompt
```

### Development Setup

```bash
git clone https://github.com/Samk13/ccprompt.git
cd ccprompt
uv sync
uv run ccprompt --help
```

## Usage

### first time usage

run `ccprompt` it will create a configuration file `ccprompt_config.json` in the current directory.
fill in the configuration file with the required information. Alternatively, you can pass the required information as command-line arguments.
`ccprompt --config CONFIG`. The configuration file should be in the following format:

```json
{
    "target_name": ["YourClassName", "your_function_name"],
    "project_path": "/full/path/to/project",
    "venv_site_packages_path": "/full/path/to/venv/lib/python3.x/site-packages",
    "exclude_venv": false,
    "output_file": "extracted_code.txt",
    "language": "python"
}

```

then run `ccprompt`, it will extract the code context based on the configuration file. and create `extracted_code.txt` that include extracted code context.

the extracted code will include file path, functions or classes and their inheritance chains.

Star and share the repository if you find it useful.

```bash
# Update your configuration file then run
ccprompt

# Also possible to pass the configuration file as arguments
ccprompt --target_names YourClassName your_function_name

# See all available options
ccprompt --help
```

## Development

### Quick Start

```bash
# Install dependencies
uv sync

# Run tests
make test

# Check code style
make lint-check

# See all available commands
make help
```

### Available Make Commands

```bash
# Dependencies and Setup
make sync        # Install dependencies with uv
make install     # Alias for sync
make clean       # Remove build artifacts and cache

# Development
make run         # Run ccprompt with debug logging
make test        # Run test suite with pytest
make build       # Build distribution packages

# Code Quality
make lint-check  # Check code style with ruff
make lint-fix    # Fix code style issues with ruff
make format      # Format and fix code with ruff

# Utilities
make change-log  # Show changes since last tag
make help        # Show all available commands
```

## Requirements

- Python >=3.12
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Project Structure

This project uses modern Python packaging with:
- **`pyproject.toml`** - Project configuration and dependencies
- **`uv`** - Fast Python package manager
- **`pytest`** - Testing framework  
- **`ruff`** - Code formatting and linting
- **`hatchling`** - Build backend
