# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import os
import json
import sys


class Config:
    def __init__(self, config_file, args):
        self.config_file = config_file
        self.args = args
        self.load_config()

    def load_config(self):
        default_config = {
            "target_name": [],
            "project_path": os.getcwd(),
            "venv_site_packages_path": "",
            "exclude_venv": False,
            "output_file": "extracted_code.txt",
            "language": "python",
        }

        # If config file does not exist or is empty, create it with default config
        config_needs_creation = False
        if not os.path.exists(self.config_file):
            config_needs_creation = True
            print(
                f"No configuration file found. Creating default config file at {self.config_file}."
            )
        else:
            if os.path.getsize(self.config_file) == 0:
                config_needs_creation = True
                print(
                    f"Configuration file {self.config_file} is empty. Writing default configurations."
                )

        if config_needs_creation:
            try:
                with open(self.config_file, "w") as f:
                    json.dump(default_config, f, indent=4)
            except Exception as e:
                print(
                    f"Error creating default configuration file {self.config_file}: {e}"
                )
                sys.exit(1)

        # Load existing config file
        try:
            with open(self.config_file, "r") as f:
                config_content = f.read()
                config = json.loads(config_content)
        except Exception as e:
            print(f"Error loading configuration file {self.config_file}: {e}")
            sys.exit(1)

        # Override configurations with command-line arguments if provided
        self.target_name = (
            self.args.target_names
            if self.args.target_names
            else config.get("target_name", [])
        )
        self.project_path = (
            self.args.project_path
            if self.args.project_path
            else config.get("project_path", "")
        )
        self.exclude_venv = self.args.exclude_venv or config.get("exclude_venv", False)
        venv_path = config.get("venv_site_packages_path", "")
        self.venv_site_packages_path = None if self.exclude_venv else venv_path
        self.output_file = (
            self.args.output_file
            if self.args.output_file
            else config.get("output_file", "extracted_code.txt")
        )
        self.language = (
            self.args.language
            if self.args.language
            else config.get("language", "python")
        )

        # Ensure target_name is a list
        if isinstance(self.target_name, str):
            self.target_name = self.target_name.split(",")

        # Check if required configurations are provided
        if not self.target_name or not self.project_path:
            print(
                "\nError: You must provide both function/class names and a project path in the configuration file or via command-line arguments."
            )
            print(
                f"Please update the configuration file at {self.config_file} or provide the required parameters via command-line.\n"
            )
            print("Example command-line usage:")
            print(
                "  ccprompt --target_names MyFunction MyClass --project_path /path/to/project\n"
            )
            sys.exit(1)
