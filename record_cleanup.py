#!/usr/bin/env python3
""" Delete AWS Route53 resource record sets """

import argparse
import os
import sys

from typing import Optional, List

import boto3
import botocore

import src


def _get_cli_args(args: Optional[List[str]] = None,
                  description: Optional[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=description,
        usage=argparse.SUPPRESS
    )
    parser.add_argument(
        '--aws-access-key-id',
        dest='key_id',
        default=os.getenv('AWS_ACCESS_KEY_ID'),
        required=not os.getenv('AWS_ACCESS_KEY_ID'),
        help='AWS access key ID'
    )
    parser.add_argument(
        '--aws-secret-access-key',
        dest='access_key',
        default=os.getenv('AWS_SECRET_ACCESS_KEY'),
        required=not os.getenv('AWS_SECRET_ACCESS_KEY'),
        help='AWS secret access key'
    )
    parser.add_argument(
        '--aws-session-token',
        dest='session_token',
        default=os.getenv('AWS_SESSION_TOKEN'),
        help='AWS session token (Multi-Factor-Authentication)'
    )
    parser.add_argument(
        '--aws-hosted-zone',
        dest='zone_name',
        default=os.getenv('AWS_ROUTE53_ZONE_NAME'),
        required=not os.getenv('AWS_ROUTE53_ZONE_NAME'),
        help='Route53 hosted zone name'
    )
    parser.add_argument(
        '--regex',
        dest='regex',
        default=r'^\w{4}-.+?\.sub\.domain\.co',
        help='Match resource records to delete based on an regex'
    )
    parser.add_argument(
        '--change-batch',
        dest='batch',
        default=200,
        type=src.batch,
        help='Maximum number of records in the change set'
    )
    parser.add_argument(
        '--dryrun',
        dest='dryrun',
        action='store_true',
        help='Dry-run mode, do not delete the resource record sets'
    )
    return parser.parse_args(args=args)


def main(argv: Optional[List[str]] = None) -> int:
    logger = src.get_logger(__name__, fmt='[%(levelname)s]: %(message)s')
    try:
        args = _get_cli_args(args=argv, description=__doc__)
        with src.AWSRoute53() as client:
            client.connect(
                aws_access_key_id=args.key_id,
                aws_secret_access_key=args.access_key,
                aws_session_token=args.session_token
            )
            records = client.get_resource_records_sets(
                args.zone_name
            )
            records = src.match_resource_records(
                records, fr'{args.regex}'
            )
            if args.dryrun:
                src.dry_run(records)
                return 0
            client.delete_resource_records_sets(
                args.zone_name,
                records=records,
                batch_size=args.batch
            )
    except KeyboardInterrupt:
        logger.info('Keyboard interrupted, aborting')
        return 0
    except (botocore.exceptions.ClientError,
            boto3.exceptions.Boto3Error) as err:
        logger.error(err)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
