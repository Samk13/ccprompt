# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import sys
import importlib
import inspect
import ast
import warnings
from pathlib import Path
from .base_parser import BaseParser


class PythonParser(BaseParser):
    def __init__(self, logger=None):
        self.logger = logger

    def build_index(self, project_path):
        index = {}
        project_path = Path(project_path)
        for py_file in project_path.rglob("*.py"):
            module_name = self.get_module_name(py_file, project_path)
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    file_content = f.read()
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    tree = ast.parse(file_content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        fq_name = f"{module_name}.{node.name}"
                        index.setdefault(node.name, []).append(fq_name)
                # Also index fully qualified names
                index.setdefault(module_name, []).append(module_name)
            except (SyntaxError, ValueError, UnicodeDecodeError):
                continue
        return index

    def get_module_name(self, file_path, project_path):
        relative_path = file_path.relative_to(project_path)
        module_parts = relative_path.with_suffix("").parts
        return ".".join(module_parts)

    def get_object_source_and_inheritance(
        self, target_name, visited_classes, directories, index
    ):
        source_codes = []

        # Ensure the directories are in sys.path
        for directory in directories:
            directory = str(Path(directory).resolve())
            if directory not in sys.path:
                sys.path.insert(0, directory)

        module_names = index.get(target_name)
        if not module_names:
            if self.logger:
                self.logger.warning(f"Target '{target_name}' not found in index.")
            return source_codes

        for fq_name in module_names:
            try:
                module_name, obj_name = fq_name.rsplit(".", 1)
            except ValueError:
                module_name = fq_name
                obj_name = None

            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                if self.logger:
                    self.logger.warning(f"Could not import module '{module_name}': {e}")
                continue

            if obj_name:
                try:
                    obj = getattr(module, obj_name)
                except AttributeError:
                    continue
            else:
                obj = module

            if inspect.isclass(obj):
                source_codes.extend(
                    self.process_class(obj, visited_classes, directories)
                )
            elif inspect.isfunction(obj) or inspect.ismethod(obj):
                source_codes.extend(self.process_function(obj))
            else:
                if self.logger:
                    self.logger.warning(
                        f"Object '{target_name}' is neither a class nor a function."
                    )
        return source_codes

    def process_class(self, obj, visited_classes, directories):
        source_codes = []
        if obj in visited_classes:
            return source_codes
        visited_classes.add(obj)
        try:
            class_source = inspect.getsource(obj)
            class_file = inspect.getsourcefile(obj)
            source_codes.append((class_file, class_source))
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not retrieve source for '{obj}': {e}")
            return source_codes

        # Process base classes
        for base_class in obj.__bases__:
            if base_class in visited_classes:
                continue
            if base_class.__module__ == "builtins":
                continue
            source_codes.extend(
                self.process_class(base_class, visited_classes, directories)
            )

        # Process metaclass if it exists and is not 'type'
        metaclass = self.get_metaclass(obj)
        if metaclass and metaclass not in visited_classes and metaclass is not type:
            if metaclass.__module__ != "builtins":
                source_codes.extend(
                    self.process_class(metaclass, visited_classes, directories)
                )

        return source_codes

    def get_metaclass(self, cls):
        # Try to get the metaclass from __metaclass__ attribute (Python 2)
        metaclass = getattr(cls, "__metaclass__", None)
        # For Python 3, use type(cls)
        if metaclass is None:
            metaclass = type(cls)
        # If the metaclass is 'type', ignore it
        if metaclass is type:
            return None
        return metaclass

    def process_function(self, obj):
        source_codes = []
        try:
            func_source = inspect.getsource(obj)
            func_file = inspect.getsourcefile(obj)
            source_codes.append((func_file, func_source))
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not retrieve source for '{obj}': {e}")
        return source_codes

    def find_definitions(self, name, directories):
        return []

    def find_inheritance_chain(self, class_name, directories):
        return []
