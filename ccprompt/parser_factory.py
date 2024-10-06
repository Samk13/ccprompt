# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import sys
from .parsers.python_parser import PythonParser
from .parsers.javascript_parser import JavaScriptParser


class ParserFactory:
    @staticmethod
    def get_parser(language, logger=None):
        if language == "python":
            return PythonParser(logger=logger)
        elif language == "javascript":
            try:
                return JavaScriptParser(logger=logger)
            except ImportError as e:
                if logger:
                    logger.error(e)
                else:
                    print(e)
                sys.exit(1)
        else:
            raise ValueError(f"Unsupported language: {language}")
