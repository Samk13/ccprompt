# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import argparse
import logging
from pathlib import Path
from .config import Config
from .parser_factory import ParserFactory
from ccprompt import __version__
from ccprompt.utils import time_it


@time_it
def extract_code(
    target_names,
    project_path,
    venv_site_packages_path=None,
    output_file="extracted_code.txt",
    language="python",
    logger=None,
):
    if logger is None:
        logger = logging.getLogger(__name__)

    output_content = []
    visited_classes = set()
    search_directories = [project_path]
    if venv_site_packages_path:
        search_directories.append(venv_site_packages_path)

    parser = ParserFactory.get_parser(language, logger=logger)

    # Build index of class and function names to module paths
    index = parser.build_index(project_path)

    for target_name in target_names:
        logger.info(f"Processing '{target_name}'...")
        source_codes = parser.get_object_source_and_inheritance(
            target_name, visited_classes, search_directories, index
        )
        if source_codes:
            for file_path, code_snippet in source_codes:
                output_content.append(f"File: {file_path}\n\n{code_snippet}\n")
        else:
            logger.warning(f"'{target_name}' not found.")

    output_path = Path(output_file)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for content in output_content:
                f.write(f"{content}\n")
        logger.info(f"Relevant code extracted to {output_path}")
    except Exception as e:
        logger.error(f"Error writing to output file {output_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract code context for AI prompts based on a function or class name."
    )
    parser.add_argument("--version", action="version", version=f"{__version__}")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the configuration JSON file.",
        default="ccprompt_config.json",
    )
    parser.add_argument(
        "--project_path",
        type=str,
        help="Override the project path from the configuration file.",
    )
    parser.add_argument(
        "--target_names",
        type=str,
        nargs="+",
        help="Override the function or class names from the configuration file.",
    )
    parser.add_argument(
        "--exclude_venv",
        action="store_true",
        help="Exclude the virtual environment site-packages directory from the search.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="Specify the output file for the extracted code.",
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["python", "javascript"],
        help="Specify the programming language.",
        default="python",
    )
    parser.add_argument(
        "--log_level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging level.",
        default="WARNING",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    logger = logging.getLogger(__name__)

    config = Config(args.config, args)

    extract_code(
        config.target_name,
        config.project_path,
        config.venv_site_packages_path,
        config.output_file,
        config.language,
        logger=logger,
    )


if __name__ == "__main__":
    main()
