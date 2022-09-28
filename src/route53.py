""" AWS (DNS) Route53 low level operations """

import boto3

from .exceptions import HostedZoneNotFoundError
from .utils import get_logger


class AWSRoute53:
    """ AWS Route53 (DNS) service """

    def __init__(self):
        self._client = None
        self.logger = get_logger(self.__class__.__name__)

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    @property
    def _rr_changed_waiter(self):
        return self._client.get_waiter(
            'resource_record_sets_changed'
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def connect(self, **kwargs):
        if self._client is None:
            access_key_id = kwargs.get('aws_access_key_id')
            secret_access_key = kwargs.get('aws_secret_access_key')
            session_token = kwargs.get('aws_session_token')
            self._client = boto3.client(
                'route53',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                aws_session_token=session_token
            )

    def _get_hosted_zone_id(self, zone_name):
        if not zone_name.endswith('.'):
            zone_name += '.'
        response = self._client.list_hosted_zones()
        for zone in response['HostedZones']:
            if zone_name == zone['Name']:
                return zone['Id']
        raise HostedZoneNotFoundError(
            f"'{zone_name}' zone does not exist"
        )

    def delete_resource_records_sets(self, zone_name, records=None, batch_size=100):
        if records is None:
            records = []
        zone_id = self._get_hosted_zone_id(zone_name)
        for i in range(0, len(records), batch_size):
            change_batch = []
            for record in records[i:i + batch_size]:
                change_batch.append({
                    'Action': 'DELETE',
                    'ResourceRecordSet': record
                })
            response = self._client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch={
                    'Changes': change_batch
                }
            )
            self.logger.info(response)
            self._wait_for_resource_record_change(response)

    def get_resource_records_sets(
        self, zone_name, record_name='*',
        record_type='A', max_items='5000'
    ):
        records = []
        zone_id = self._get_hosted_zone_id(zone_name)
        while True:
            response = self._client.list_resource_record_sets(
                HostedZoneId=zone_id,
                StartRecordName=record_name,
                StartRecordType=record_type,
                MaxItems=str(max_items)
            )
            records.extend(list(response['ResourceRecordSets']))
            try:
                record_name = response['NextRecordName']
                record_type = response['NextRecordType']
            except KeyError:
                return records
            else:
                max_items = int(int(max_items) - 300)
                if max_items <= 0:
                    break
        return records

    def _wait_for_resource_record_change(self, result, delay=10, max_attempts=30):
        request_id = result["ChangeInfo"]["Id"]
        self._rr_changed_waiter.wait(
            Id=request_id,
            WaiterConfig={
                "Delay": delay,
                "MaxAttempts": max_attempts
            }
        )

    def _resource_record_exists(self, zone_name, record_name):
        zone_id = self._get_hosted_zone_id(zone_name)
        response = self._client.list_resource_record_sets(
            HostedZoneId=zone_id,
            StartRecordName=record_name,
            MaxItems='1'
        )
        record = response['ResourceRecordSets'][0]
        return record['Name'] == record_name

    def close(self):
        if self._client is not None:
            self._client.close()
