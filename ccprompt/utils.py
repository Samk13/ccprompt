# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

import time


def time_it(func):
    """Decorator to measure the time taken for a function to execute."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger = kwargs.get("logger")
        if logger:
            logger.info(f"Time taken for process: {elapsed_time:.2f} seconds")
        else:
            print(f"Time taken for process: {elapsed_time:.2f} seconds")
        return result

    return wrapper
