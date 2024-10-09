# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import argparse
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
    """
    Extract relevant code based on a list of function or class names.
    Include all their inheritance and related upper-level code.
    """
    if logger is None:
        import logging

        logger = logging.getLogger(__name__)

    output_content = []
    visited_classes = set()
    search_directories = [project_path]
    if venv_site_packages_path:
        search_directories.append(venv_site_packages_path)

    parser = ParserFactory.get_parser(language)

    # Extract the requested classes or functions
    for target_name in target_names:
        found = False
        logger.info(f"Searching for '{target_name}'...")
        for file_path, code_snippet, extra_info in parser.find_definitions(
            target_name, search_directories
        ):
            if file_path is None:
                continue  # Target not found
            found = True
            if extra_info == "class":
                # Target is a class
                logger.debug(f"Found class '{target_name}' in {file_path}")
                output_content.append(f"File: {file_path}\n\n{code_snippet}\n")
                visited_classes.add(target_name)
                # Get the inheritance chain
                inheritance_chain = parser.find_inheritance_chain(
                    target_name, search_directories
                )
                for class_file_path, class_source in inheritance_chain:
                    class_definition_line = class_source.split("\n")[0]
                    class_name_part = class_definition_line.split("(")[0].split(" ")[
                        1
                    ]  # Extract class name from definition
                    if class_name_part not in visited_classes:
                        output_content.append(
                            f"File: {class_file_path}\n\n{class_source}\n"
                        )
                        visited_classes.add(class_name_part)
            else:
                # Target is a function
                code_snippet, class_hierarchy = code_snippet, extra_info
                logger.debug(f"Found function '{target_name}' in {file_path}")
                if class_hierarchy:
                    # Function is inside a class
                    class_name = class_hierarchy[-1]
                    if class_name not in visited_classes:
                        logger.debug(f"Processing class '{class_name}'")
                        # Get the class definition and inheritance chain
                        inheritance_chain = parser.find_inheritance_chain(
                            class_name, search_directories
                        )
                        for class_file_path, class_source in inheritance_chain:
                            class_definition_line = class_source.split("\n")[0]
                            class_name_part = class_definition_line.split("(")[0].split(
                                " "
                            )[1]  # Extract class name from definition
                            if class_name_part not in visited_classes:
                                output_content.append(
                                    f"File: {class_file_path}\n\n{class_source}\n"
                                )
                                visited_classes.add(class_name_part)
                    # Include the function code
                    output_content.append(f"File: {file_path}\n\n{code_snippet}\n")
                else:
                    # Function is not inside a class
                    output_content.append(f"File: {file_path}\n\n{code_snippet}\n")

        if not found:
            logger.warning(f"'{target_name}' not found in the provided directories.")

    # Write to output file
    output_path = Path(output_file)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for line in output_content:
                f.write(f"{line}\n")
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

    # Set up logging
    import logging

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    logger = logging.getLogger(__name__)

    # Load configuration
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
