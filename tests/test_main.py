# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import unittest
from pathlib import Path
from ccprompt.main import extract_code
from unittest.mock import patch, MagicMock


class TestExtractCode(unittest.TestCase):
    @patch("ccprompt.main.ParserFactory.get_parser")
    @patch("ccprompt.main.open", new_callable=unittest.mock.mock_open)
    def test_extract_code(self, mock_open, mock_get_parser):
        mock_parser = MagicMock()
        mock_get_parser.return_value = mock_parser
        mock_parser.build_index.return_value = {"TestClass": ["test_module.TestClass"]}
        mock_parser.get_object_source_and_inheritance.return_value = [
            ("test_project/test_module.py", "class TestClass: pass")
        ]

        target_names = ["TestClass"]
        project_path = "test_project"
        venv_site_packages_path = None
        output_file = "extracted_code.txt"
        language = "python"
        logger = MagicMock()

        extract_code(
            target_names,
            project_path,
            venv_site_packages_path,
            output_file,
            language,
            logger,
        )

        mock_get_parser.assert_called_once_with(language, logger=logger)
        mock_parser.build_index.assert_called_once_with(project_path)
        mock_parser.get_object_source_and_inheritance.assert_called_once_with(
            "TestClass", set(), [project_path], {"TestClass": ["test_module.TestClass"]}
        )
        mock_open.assert_called_once_with(Path(output_file), "w", encoding="utf-8")
        mock_open().write.assert_called_once_with(
            "File: test_project/test_module.py\n\nclass TestClass: pass\n\n"
        )

    @patch("ccprompt.main.ParserFactory.get_parser")
    @patch("ccprompt.main.open", new_callable=unittest.mock.mock_open)
    def test_extract_code_with_venv(self, mock_open, mock_get_parser):
        mock_parser = MagicMock()
        mock_get_parser.return_value = mock_parser
        mock_parser.build_index.return_value = {"TestClass": ["test_module.TestClass"]}
        mock_parser.get_object_source_and_inheritance.return_value = [
            ("test_project/test_module.py", "class TestClass: pass")
        ]

        target_names = ["TestClass"]
        project_path = "test_project"
        venv_site_packages_path = "venv/lib/python3.8/site-packages"
        output_file = "extracted_code.txt"
        language = "python"
        logger = MagicMock()

        extract_code(
            target_names,
            project_path,
            venv_site_packages_path,
            output_file,
            language,
            logger,
        )

        mock_get_parser.assert_called_once_with(language, logger=logger)
        mock_parser.build_index.assert_called_once_with(project_path)
        mock_parser.get_object_source_and_inheritance.assert_called_once_with(
            "TestClass",
            set(),
            [project_path, venv_site_packages_path],
            {"TestClass": ["test_module.TestClass"]},
        )
        mock_open.assert_called_once_with(Path(output_file), "w", encoding="utf-8")
        mock_open().write.assert_called_once_with(
            "File: test_project/test_module.py\n\nclass TestClass: pass\n\n"
        )

    @patch("ccprompt.main.ParserFactory.get_parser")
    @patch("ccprompt.main.open", new_callable=unittest.mock.mock_open)
    def test_extract_code_not_found(self, mock_open, mock_get_parser):
        mock_parser = MagicMock()
        mock_get_parser.return_value = mock_parser
        mock_parser.build_index.return_value = {"TestClass": ["test_module.TestClass"]}
        mock_parser.get_object_source_and_inheritance.return_value = []

        target_names = ["NonExistentClass"]
        project_path = "test_project"
        venv_site_packages_path = None
        output_file = "extracted_code.txt"
        language = "python"
        logger = MagicMock()

        extract_code(
            target_names,
            project_path,
            venv_site_packages_path,
            output_file,
            language,
            logger,
        )

        mock_get_parser.assert_called_once_with(language, logger=logger)
        mock_parser.build_index.assert_called_once_with(project_path)
        mock_parser.get_object_source_and_inheritance.assert_called_once_with(
            "NonExistentClass",
            set(),
            [project_path],
            {"TestClass": ["test_module.TestClass"]},
        )
        mock_open.assert_called_once_with(Path(output_file), "w", encoding="utf-8")
        mock_open().write.assert_not_called()
        logger.warning.assert_called_once_with("'NonExistentClass' not found.")


if __name__ == "__main__":
    unittest.main()
