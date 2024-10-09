# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def find_definitions(self, name, directories):
        pass

    @abstractmethod
    def find_inheritance_chain(self, class_name, directories):
        pass
