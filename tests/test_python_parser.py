# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from ccprompt.parsers.python_parser import PythonParser


class TestPythonParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_path = Path(self.test_dir)
        self.logger = None  # Replace with a logger if needed
        self.parser = PythonParser(logger=self.logger)

        # Insert the project path into sys.path before creating test files
        sys.path.insert(0, str(self.project_path))
        self.create_test_files()

    def tearDown(self):
        # Remove the test directory from sys.path
        if str(self.project_path) in sys.path:
            sys.path.remove(str(self.project_path))
        shutil.rmtree(self.test_dir)

    def create_test_files(self):
        # Create __init__.py to make the directory a package
        (self.project_path / "__init__.py").touch()

        # Create metaclass file
        metaclass_code = """
class MyMeta(type):
    def __new__(cls, name, bases, attrs):
        return super(MyMeta, cls).__new__(cls, name, bases, attrs)
"""
        metaclass_file = self.project_path / "metaclass.py"
        with open(metaclass_file, "w") as f:
            f.write(metaclass_code)

        # Create base class file
        base_class_code = """
from metaclass import MyMeta

class BaseClass(metaclass=MyMeta):
    def base_method(self):
        pass
"""
        base_class_file = self.project_path / "base_class.py"
        with open(base_class_file, "w") as f:
            f.write(base_class_code)

        # Create derived class file
        derived_class_code = """
from base_class import BaseClass

class DerivedClass(BaseClass):
    def derived_method(self):
        pass
"""
        derived_class_file = self.project_path / "derived_class.py"
        with open(derived_class_file, "w") as f:
            f.write(derived_class_code)

    def test_build_index(self):
        index = self.parser.build_index(self.project_path)
        expected_classes = {"MyMeta", "BaseClass", "DerivedClass"}
        self.assertTrue(expected_classes.issubset(set(index.keys())))

    def test_get_module_name(self):
        file_path = self.project_path / "subdir" / "module.py"
        os.makedirs(file_path.parent, exist_ok=True)
        module_name = self.parser.get_module_name(file_path, self.project_path)
        self.assertEqual(module_name, "subdir.module")

    def test_process_function(self):
        # Add a function to the derived_class.py file
        function_code = """
def test_function():
    return "Hello, World!"
"""
        with open(self.project_path / "derived_class.py", "a") as f:
            f.write(function_code)

        # Remove 'derived_class' from sys.modules to force reload
        if "derived_class" in sys.modules:
            del sys.modules["derived_class"]


if __name__ == "__main__":
    unittest.main()
