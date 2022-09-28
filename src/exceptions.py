""" package exceptions """

import boto3


class HostedZoneNotFoundError(boto3.exceptions.Boto3Error):
    """ Route53 hosted zone does not exist error """
