# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import os
import ast
import warnings
from .base_parser import BaseParser

class PythonParser(BaseParser):
    def __init__(self, logger=None):
        self.file_handler = FileHandler()
        self.definition_finder = DefinitionFinder()
        self.logger = logger

    def find_definitions(self, name, directories):
        files = self.file_handler.get_python_files(directories, name)
        for file_path, file_content in files:
            definitions = self.definition_finder.find_definitions_in_content(name, file_content)
            for def_info in definitions:
                def_type, code_snippet, class_hierarchy = def_info
                yield file_path, code_snippet, class_hierarchy or def_type

    def find_class_definition(self, class_name, directories):
        files = self.file_handler.get_python_files(directories, class_name)
        for file_path, file_content in files:
            class_node = self.definition_finder.find_class_node(class_name, file_content)
            if class_node:
                class_source = ast.get_source_segment(file_content, class_node)
                return file_path, class_source, class_node
        return None  # Return None when the class is not found

    def find_inheritance_chain(self, class_name, directories):
        inheritance_chain = []
        classes_to_trace = [class_name]
        visited_classes = set()

        while classes_to_trace:
            current_class = classes_to_trace.pop()
            if current_class in visited_classes:
                continue
            visited_classes.add(current_class)

            result = self.find_class_definition(current_class, directories)
            if result:
                file_path, class_source, class_node = result
                inheritance_chain.append((file_path, class_source))
                base_classes = self.definition_finder.get_base_classes(class_node)
                for base_class in base_classes:
                    if base_class not in visited_classes:
                        classes_to_trace.append(base_class)
            else:
                # Class definition not found
                if self.logger:
                    self.logger.warning(f"Class or metaclass '{current_class}' not found in provided directories.")
                else:
                    print(f"Warning: Class or metaclass '{current_class}' not found in provided directories.")
                continue
        return inheritance_chain

# Helper Classes

class FileHandler:
    def get_python_files(self, directories, name_filter=None):
        for directory in directories:
            for root, _, files in os.walk(directory):
                python_files = [file for file in files if file.endswith('.py')]
                for file in python_files:
                    file_path = os.path.join(root, file)
                    file_content = None
                    # Try reading with UTF-8 encoding
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                    except UnicodeDecodeError:
                        # Try reading with UTF-16 encoding
                        try:
                            with open(file_path, 'r', encoding='utf-16') as f:
                                file_content = f.read()
                        except UnicodeDecodeError:
                            # Skip files that can't be decoded
                            continue
                    except (IOError, OSError):
                        continue  # Skip files that can't be read

                    if file_content is not None:
                        if name_filter and name_filter not in file_content:
                            continue  # Skip files that don't contain the target name
                        yield file_path, file_content


class DefinitionFinder:
    def find_definitions_in_content(self, target_name, file_content):
        definitions = []
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(file_content)
            visitor = DefinitionVisitor(target_name, file_content)
            visitor.visit(tree)
            for def_info in visitor.found_definitions:
                definitions.append(def_info)
        except (SyntaxError, ValueError):
            pass  # Skip files with syntax errors
        return definitions

    def find_class_node(self, class_name, file_content):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(file_content)
            visitor = ClassNodeVisitor(class_name)
            visitor.visit(tree)
            return visitor.class_node
        except (SyntaxError, ValueError):
            pass
        return None

    def get_base_classes(self, class_node):
        base_classes = []

        # Process base classes
        for base in class_node.bases:
            base_class_name = self.get_full_name(base)
            if base_class_name:
                base_classes.append(base_class_name)

        # Process metaclass
        for keyword in class_node.keywords:
            if keyword.arg == 'metaclass':
                metaclass_name = self.get_full_name(keyword.value)
                if metaclass_name:
                    base_classes.append(metaclass_name)

        return base_classes

    def get_full_name(self, node):
        """
        Helper method to get the full name from an AST node representing a class or metaclass.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            names = []
            current = node
            while isinstance(current, ast.Attribute):
                names.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                names.insert(0, current.id)
                return '.'.join(names)
        # Return None for unsupported node types
        return None

class DefinitionVisitor(ast.NodeVisitor):
    def __init__(self, target_name, source_code):
        self.target_name = target_name
        self.source_code = source_code
        self.found_definitions = []
        self.class_hierarchy = []

    def visit_ClassDef(self, node):
        if node.name == self.target_name:
            code_snippet = self.get_code_snippet(node)
            self.found_definitions.append(('class', code_snippet, None))
        self.class_hierarchy.append(node.name)
        self.generic_visit(node)
        self.class_hierarchy.pop()

    def visit_FunctionDef(self, node):
        if node.name == self.target_name:
            code_snippet = self.get_code_snippet(node)
            hierarchy = list(self.class_hierarchy)
            self.found_definitions.append(('function', code_snippet, hierarchy))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def get_code_snippet(self, node):
        return ast.get_source_segment(self.source_code, node)

class ClassNodeVisitor(ast.NodeVisitor):
    def __init__(self, class_name):
        self.class_name = class_name
        self.class_node = None

    def visit_ClassDef(self, node):
        if node.name == self.class_name:
            self.class_node = node
            return  # Found the class, stop visiting
        self.generic_visit(node)
