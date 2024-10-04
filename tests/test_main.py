# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import unittest
import os
import tempfile
from unittest.mock import patch
from ccprompt.main import extract_code
from ccprompt.parser_factory import ParserFactory
import logging

class TestMain(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to hold test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = self.test_dir.name

        # Sample Python code for testing
        self.sample_code = '''
class BaseClass:
    pass

class DerivedClass(BaseClass):
    pass

def standalone_function():
    pass

class SampleClass:
    def method_function(self):
        pass
'''

        # Write sample file to the temporary directory
        self.write_test_file('test_code.py', self.sample_code)

        # Prepare the logger
        self.logger = logging.getLogger('test_logger')
        self.logger.setLevel(logging.DEBUG)
        self.log_stream = logging.StreamHandler()
        self.logger.addHandler(self.log_stream)

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()
        self.logger.removeHandler(self.log_stream)

    def write_test_file(self, filename, content, encoding='utf-8'):
        file_path = os.path.join(self.test_path, filename)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)

    @patch('ccprompt.main.Path')
    def test_extract_code_class(self, mock_path):
        # Mock the output file path
        mock_output = tempfile.NamedTemporaryFile(delete=False)
        mock_path.return_value = mock_output.name

        # Call extract_code to extract a class
        extract_code(
            target_names=['DerivedClass'],
            project_path=self.test_path,
            venv_site_packages_path=None,
            output_file=mock_output.name,
            language='python',
            logger=self.logger
        )

        # Read the output file
        with open(mock_output.name, 'r') as f:
            output_content = f.read()

        # Check that the class and its base class are included
        self.assertIn('class DerivedClass(BaseClass):', output_content)
        self.assertIn('class BaseClass:', output_content)

    @patch('ccprompt.main.Path')
    def test_extract_code_function(self, mock_path):
        # Mock the output file path
        mock_output = tempfile.NamedTemporaryFile(delete=False)
        mock_path.return_value = mock_output.name

        # Call extract_code to extract a function
        extract_code(
            target_names=['standalone_function'],
            project_path=self.test_path,
            venv_site_packages_path=None,
            output_file=mock_output.name,
            language='python',
            logger=self.logger
        )

        # Read the output file
        with open(mock_output.name, 'r') as f:
            output_content = f.read()

        # Check that the function is included
        self.assertIn('def standalone_function():', output_content)

    @patch('ccprompt.main.Path')
    def test_extract_code_method(self, mock_path):
        # Mock the output file path
        mock_output = tempfile.NamedTemporaryFile(delete=False)
        mock_path.return_value = mock_output.name

        # Call extract_code to extract a method
        extract_code(
            target_names=['method_function'],
            project_path=self.test_path,
            venv_site_packages_path=None,
            output_file=mock_output.name,
            language='python',
            logger=self.logger
        )

        # Read the output file
        with open(mock_output.name, 'r') as f:
            output_content = f.read()

        # Check that the method and its class are included
        self.assertIn('def method_function(self):', output_content)
        self.assertIn('class SampleClass:', output_content)

    @patch('ccprompt.main.Path')
    def test_extract_code_nonexistent(self, mock_path):
        # Mock the output file path
        mock_output = tempfile.NamedTemporaryFile(delete=False)
        mock_path.return_value = mock_output.name

        # Call extract_code with a non-existent target
        extract_code(
            target_names=['nonexistent_function'],
            project_path=self.test_path,
            venv_site_packages_path=None,
            output_file=mock_output.name,
            language='python',
            logger=self.logger
        )

        # Read the output file
        with open(mock_output.name, 'r') as f:
            output_content = f.read()

        # The output should be empty
        self.assertEqual(output_content.strip(), '')

        # Check that a warning was logged
        # (Assuming the logger writes to the console or a stream we can capture)

if __name__ == '__main__':
    unittest.main()
