# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

try:
    import esprima
except ImportError:
    esprima = None

from .js_parser_interface import JSParserInterface


class EsprimaAdapter(JSParserInterface):
    def parse(self, code):
        if esprima is None:
            raise ImportError(
                "The 'esprima' library is required for JavaScript/TypeScript parsing. Please install it using 'pip install esprima'."
            )
        return esprima.parseScript(code, tolerant=True, range=True)
