""" Utility functions """

import argparse
import logging
import re
import sys
import os
import pydoc
from typing import (
    Optional,
    Union,
    List,
    Dict,
    Any
)


def match_resource_records(
    records: List[Dict[str, Any]],
    regex: Optional[str] = None
) -> List[Dict[str, Any]]:
    if regex:
        return [
            r
            for r in records
            if re.search(regex, r['Name'])
        ]
    return records


def batch(size: int) -> int:
    size = int(size)
    if size <= 0:
        raise argparse.ArgumentTypeError(
            "must be positive number and greater than zero"
        )
    return size


def get_logger(
      name: str, level: str = 'info',
      fmt: Union[str, None] = None
    ) -> logging.Logger:
    logger = logging.getLogger(name)
    level = getattr(logging, level.upper(), 10)
    logger.setLevel(level)
    console = logging.StreamHandler(sys.stdout)
    template = logging.Formatter(fmt)
    console.setFormatter(template)
    logger.addHandler(console)
    return logger


def dry_run(records: Optional[List[Dict[str, Any]]] = None) -> None:
    if records is None:
        records = []
    pydoc.pager(
        os.linesep.join(
            [r['Name'] for r in records]
        )
    )
