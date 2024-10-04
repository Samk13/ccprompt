# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import os
from .base_parser import BaseParser
from .esprima_adapter import EsprimaAdapter


class JavaScriptParser(BaseParser):
    def __init__(self):
        self.parser_adapter = EsprimaAdapter()

    def find_definitions(self, name, directories):
        # Same as before
        for directory in directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith((".js", ".ts")):
                        file_path = os.path.join(root, file)
                        code_snippet = self.find_function_or_class_in_file(
                            name, file_path
                        )
                        if code_snippet:
                            yield file_path, code_snippet

    def find_inheritance_chain(self, class_name, directories):
        # Same as before
        inheritance_chain = []
        classes_to_trace = [class_name]
        visited_classes = set()

        while classes_to_trace:
            current_class = classes_to_trace.pop()
            if current_class in visited_classes:
                continue
            visited_classes.add(current_class)

            file_path, class_source, super_class = self.find_class_definition(
                current_class, directories
            )
            if file_path and class_source:
                inheritance_chain.append((file_path, class_source))
                if super_class and super_class not in visited_classes:
                    classes_to_trace.append(super_class)

        return inheritance_chain

    def find_function_or_class_in_file(self, name, file_path):
        """
        Search for a function or class definition by name in a given JavaScript/TypeScript file.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                tree = self.parser_adapter.parse(file_content)
                for node in tree.body:
                    if (
                        (
                            node.type == "FunctionDeclaration"
                            or node.type == "ClassDeclaration"
                        )
                        and node.id
                        and node.id.name == name
                    ):
                        # Extract the source code
                        code_snippet = file_content[node.range[0] : node.range[1]]
                        return code_snippet
        except Exception:
            # Optionally log the error
            pass
        return None

    def find_class_definition(self, class_name, directories):
        # Same as before, using self.parser_adapter.parse()
        for directory in directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith((".js", ".ts")):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                file_content = f.read()
                                tree = self.parser_adapter.parse(file_content)
                                for node in tree.body:
                                    if (
                                        node.type == "ClassDeclaration"
                                        and node.id
                                        and node.id.name == class_name
                                    ):
                                        class_source = file_content[
                                            node.range[0] : node.range[1]
                                        ]
                                        super_class = None
                                        if node.superClass and hasattr(
                                            node.superClass, "name"
                                        ):
                                            super_class = node.superClass.name
                                        return file_path, class_source, super_class
                        except Exception:
                            # Optionally log the error
                            pass
        return None, None, None
