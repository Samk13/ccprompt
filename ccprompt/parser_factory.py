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
    def get_parser(language):
        if language == "python":
            return PythonParser()
        elif language == "javascript":
            try:
                return JavaScriptParser()
            except ImportError as e:
                print(e)
                sys.exit(1)
        else:
            raise ValueError(f"Unsupported language: {language}")
