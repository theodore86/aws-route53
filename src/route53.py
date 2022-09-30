""" AWS (DNS) Route53 low level operations """

from types import TracebackType
from typing import (
    Dict,
    Any,
    Union,
    List,
    Optional,
    TypeVar,
    Type
)

import boto3
from botocore.waiter import Waiter

from .exceptions import HostedZoneNotFoundError
from .utils import get_logger

R = TypeVar('R', bound='AWSRoute53')


class AWSRoute53:
    """ AWS Route53 (DNS) service """

    def __init__(self: R) -> None:
        self._client: boto3.Session = None
        self.logger = get_logger(self.__class__.__name__)

    def __repr__(self: R) -> str:
        return f'{self.__class__.__name__}()'

    @property
    def _rr_changed_waiter(self: R) -> Waiter:
        return self._client.get_waiter(
            'resource_record_sets_changed'
        )

    def __enter__(self: R) -> R:
        return self

    def __exit__(self: R, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]
    ) -> None:
        return self.close()

    def connect(self: R, **kwargs: Dict[str, str]) -> boto3.Session:
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

    def _get_hosted_zone_id(self: R, zone_name: str) -> str:
        if not zone_name.endswith('.'):
            zone_name += '.'
        response = self._client.list_hosted_zones()
        for zone in response['HostedZones']:
            if zone_name == zone['Name']:
                return zone['Id']
        raise HostedZoneNotFoundError(
            f"'{zone_name}' zone does not exist"
        )

    def delete_resource_records_sets(
        self: R, zone_name: str,
        records: Optional[List[Dict[str, Any]]]=None,
        batch_size: int =100
    ) -> None:
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
        self: R, zone_name: str, record_name: str ='*',
        record_type: str ='A',
        max_items: Union[int, str] = '5000'
    ) -> List[Dict[str, Any]]:
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

    def _wait_for_resource_record_change(
            self, result: Dict[str, Any],
            delay: int = 10, max_attempts: int = 30
    ) -> None:
        request_id = result["ChangeInfo"]["Id"]
        self._rr_changed_waiter.wait(
            Id=request_id,
            WaiterConfig={
                "Delay": delay,
                "MaxAttempts": max_attempts
            }
        )

    def _resource_record_exists(self: R, zone_name: str, record_name: str) -> bool:
        zone_id = self._get_hosted_zone_id(zone_name)
        response = self._client.list_resource_record_sets(
            HostedZoneId=zone_id,
            StartRecordName=record_name,
            MaxItems='1'
        )
        record = response['ResourceRecordSets'][0]
        return record['Name'] == record_name

    def close(self: R) -> None:
        if self._client is not None:
            self._client.close()
