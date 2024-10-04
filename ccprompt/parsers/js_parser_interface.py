# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

from abc import ABC, abstractmethod


class JSParserInterface(ABC):
    @abstractmethod
    def parse(self, code):
        pass
