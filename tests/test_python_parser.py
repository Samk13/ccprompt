# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import ast
import unittest
import os
import tempfile
import warnings
from ccprompt.parsers.python_parser import PythonParser


class TestPythonParser(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to hold test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = self.test_dir.name

        # Sample Python code for testing
        self.sample_code_class = """
class BaseClass:
    pass

class DerivedClass(BaseClass):
    pass

class Meta(type):
    pass

class MetaClass(metaclass=Meta):
    pass
"""

        self.sample_code_function = """
def standalone_function():
    pass

class SampleClass:
    def method_function(self):
        pass

    async def async_method_function(self):
        pass
"""

        self.sample_code_encoding = (
            "class EncodingTest:\n    pass\n"  # Simple code with UTF-8 encoding
        )

        # Write sample files to the temporary directory
        self.write_test_file("test_class.py", self.sample_code_class)
        self.write_test_file("test_function.py", self.sample_code_function)
        self.write_test_file(
            "test_encoding.py",
            self.sample_code_encoding.encode("utf-16"),
            encoding="utf-16",
        )

        # Initialize the parser
        self.parser = PythonParser()

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def write_test_file(self, filename, content, encoding="utf-8"):
        file_path = os.path.join(self.test_path, filename)
        with open(file_path, "w", encoding=encoding, errors="ignore") as f:
            if isinstance(content, bytes):
                content = content.decode(encoding, errors="ignore")
            f.write(content)

    def test_find_class_definition(self):
        # Test finding a class definition
        class_name = "DerivedClass"
        file_path, class_source, class_node = self.parser.find_class_definition(
            class_name, [self.test_path]
        )
        self.assertIsNotNone(file_path)
        self.assertIn(class_name, class_source)

    def test_find_function_definition(self):
        # Test finding a standalone function
        function_name = "standalone_function"
        definitions = list(
            self.parser.find_definitions(function_name, [self.test_path])
        )
        self.assertGreater(len(definitions), 0)
        file_path, code_snippet, extra_info = definitions[0]
        self.assertIn(function_name, code_snippet)
        self.assertEqual(extra_info, "function")

    def test_find_method_function(self):
        # Test finding a method inside a class
        function_name = "method_function"
        definitions = list(
            self.parser.find_definitions(function_name, [self.test_path])
        )
        self.assertGreater(len(definitions), 0)
        file_path, code_snippet, class_hierarchy = definitions[0]
        self.assertIn(function_name, code_snippet)
        self.assertIn("SampleClass", class_hierarchy)

    def test_find_async_method_function(self):
        # Test finding an async method inside a class
        function_name = "async_method_function"
        definitions = list(
            self.parser.find_definitions(function_name, [self.test_path])
        )
        self.assertGreater(len(definitions), 0)
        file_path, code_snippet, class_hierarchy = definitions[0]
        self.assertIn(function_name, code_snippet)
        self.assertIn("SampleClass", class_hierarchy)

    def test_find_inheritance_chain(self):
        # Test finding the inheritance chain of a class
        class_name = "DerivedClass"
        inheritance_chain = self.parser.find_inheritance_chain(
            class_name, [self.test_path]
        )
        self.assertEqual(len(inheritance_chain), 2)
        class_names = []
        for _, source in inheritance_chain:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                node = ast.parse(source)
            for item in node.body:
                if isinstance(item, ast.ClassDef):
                    class_names.append(item.name)
                    break  # Assuming one class per source
        self.assertIn("DerivedClass", class_names)
        self.assertIn("BaseClass", class_names)

    def test_find_metaclass_inheritance(self):
        # Test finding inheritance chain with metaclass
        class_name = "MetaClass"
        inheritance_chain = self.parser.find_inheritance_chain(
            class_name, [self.test_path]
        )
        self.assertEqual(len(inheritance_chain), 2)
        class_names = []
        for _, source in inheritance_chain:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                node = ast.parse(source)
            for item in node.body:
                if isinstance(item, ast.ClassDef):
                    class_names.append(item.name)
                    break
        self.assertIn("MetaClass", class_names)
        self.assertIn("Meta", class_names)

    def test_handle_non_utf8_encoding(self):
        # Test handling a file with non-UTF-8 encoding
        class_name = "EncodingTest"
        file_path, class_source, class_node = self.parser.find_class_definition(
            class_name, [self.test_path]
        )
        self.assertIsNotNone(file_path)
        self.assertIn(class_name, class_source)

    def test_class_not_found(self):
        # Test searching for a class that doesn't exist
        class_name = "NonExistentClass"
        result = self.parser.find_class_definition(class_name, [self.test_path])
        self.assertIsNone(result)

    def test_function_not_found(self):
        # Test searching for a function that doesn't exist
        function_name = "non_existent_function"
        definitions = list(
            self.parser.find_definitions(function_name, [self.test_path])
        )
        self.assertEqual(len(definitions), 0)

    def test_logging(self):
        # Test that logging works (simplified for testing purposes)
        import logging
        from io import StringIO

        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        # Initialize parser with logger
        parser_with_logger = PythonParser(logger=logger)

        # Attempt to find a non-existent class to trigger a warning
        class_name = "NonExistentClass"
        parser_with_logger.find_inheritance_chain(class_name, [self.test_path])

        # Check that a warning was logged
        log_contents = log_stream.getvalue()
        self.assertIn(f"Class or metaclass '{class_name}' not found", log_contents)

        # Clean up handlers
        logger.removeHandler(handler)


if __name__ == "__main__":
    unittest.main()
