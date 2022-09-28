""" Utility functions """

import argparse
import logging
import re
import sys
import os
import pydoc


def match_resource_records(records, regex=None):
    if regex:
        return [
            r
            for r in records
            if re.search(regex, r['Name'])
        ]
    return records


def batch(size):
    size = int(size)
    if size <= 0:
        raise argparse.ArgumentTypeError(
            "must be positive number and greater than zero"
        )
    return size


def get_logger(name, level='info', fmt=None):
    logger = logging.getLogger(name)
    level = getattr(logging, level.upper(), 10)
    logger.setLevel(level)
    console = logging.StreamHandler(sys.stdout)
    template = logging.Formatter(fmt)
    console.setFormatter(template)
    logger.addHandler(console)
    return logger


def dry_run(records=None):
    if records is None:
        records = []
    pydoc.pager(
        os.linesep.join(
            [r['Name'] for r in records]
        )
    )
