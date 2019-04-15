"""Redis storage end to end tests."""
#pylint: disable=no-self-use,protected-access

import json
import os

from splitio.client.util import get_metadata
from splitio.models import splits, segments, impressions, events, telemetry
from splitio.storage.redis import RedisSplitStorage, RedisSegmentStorage, RedisImpressionsStorage, \
    RedisEventsStorage, RedisTelemetryStorage
from splitio.storage.adapters.redis import _build_default_client


class SplitStorageTests(object):
    """Redis Split storage e2e tests."""

    def test_put_fetch(self):
        """Test storing and retrieving splits in redis."""
        adapter = _build_default_client({})
        try:
            storage = RedisSplitStorage(adapter)
            with open(os.path.join(os.path.dirname(__file__), 'files', 'split_changes.json'), 'r') as flo:
                split_changes = json.load(flo)

            split_objects = [splits.from_raw(raw) for raw in split_changes['splits']]
            for split_object in split_objects:
                raw = split_object.to_json()
                adapter.set(RedisSplitStorage._SPLIT_KEY.format(split_name=split_object.name), json.dumps(raw))

            original_splits = {split.name: split for split in split_objects}
            fetched_splits = {name: storage.get(name) for name in original_splits.keys()}

            assert set(original_splits.keys()) == set(fetched_splits.keys())

            for original_split in original_splits.values():
                fetched_split = fetched_splits[original_split.name]
                assert original_split.traffic_type_name == fetched_split.traffic_type_name
                assert original_split.seed == fetched_split.seed
                assert original_split.algo == fetched_split.algo
                assert original_split.status == fetched_split.status
                assert original_split.change_number == fetched_split.change_number
                assert original_split.killed == fetched_split.killed
                assert original_split.default_treatment == fetched_split.default_treatment
                for index, original_condition in enumerate(original_split.conditions):
                    fetched_condition = fetched_split.conditions[index]
                    assert original_condition.label == fetched_condition.label
                    assert original_condition.condition_type == fetched_condition.condition_type
                    assert len(original_condition.matchers) == len(fetched_condition.matchers)
                    assert len(original_condition.partitions) == len(fetched_condition.partitions)

            adapter.set(RedisSplitStorage._SPLIT_TILL_KEY, split_changes['till'])
            assert storage.get_change_number() == split_changes['till']
        finally:
            to_delete = [
                "SPLITIO.split.sample_feature",
                "SPLITIO.splits.till",
                "SPLITIO.split.all_feature",
                "SPLITIO.split.killed_feature",
                "SPLITIO.split.Risk_Max_Deductible",
                "SPLITIO.split.whitelist_feature",
                "SPLITIO.split.regex_test",
                "SPLITIO.split.boolean_test",
                "SPLITIO.split.dependency_test"
            ]
            for item in to_delete:
                adapter.delete(item)

    def test_get_all(self):
        """Test get all names & splits."""
        adapter = _build_default_client({})
        try:
            storage = RedisSplitStorage(adapter)
            with open(os.path.join(os.path.dirname(__file__), 'files', 'split_changes.json'), 'r') as flo:
                split_changes = json.load(flo)

            split_objects = [splits.from_raw(raw) for raw in split_changes['splits']]
            for split_object in split_objects:
                raw = split_object.to_json()
                adapter.set(RedisSplitStorage._SPLIT_KEY.format(split_name=split_object.name), json.dumps(raw))

            original_splits = {split.name: split for split in split_objects}
            fetched_names = storage.get_split_names()
            fetched_splits = {split.name: split for split in storage.get_all_splits()}
            assert set(fetched_names) == set(fetched_splits.keys())

            for original_split in original_splits.values():
                fetched_split = fetched_splits[original_split.name]
                assert original_split.traffic_type_name == fetched_split.traffic_type_name
                assert original_split.seed == fetched_split.seed
                assert original_split.algo == fetched_split.algo
                assert original_split.status == fetched_split.status
                assert original_split.change_number == fetched_split.change_number
                assert original_split.killed == fetched_split.killed
                assert original_split.default_treatment == fetched_split.default_treatment
                for index, original_condition in enumerate(original_split.conditions):
                    fetched_condition = fetched_split.conditions[index]
                    assert original_condition.label == fetched_condition.label
                    assert original_condition.condition_type == fetched_condition.condition_type
                    assert len(original_condition.matchers) == len(fetched_condition.matchers)
                    assert len(original_condition.partitions) == len(fetched_condition.partitions)
        finally:
            adapter.delete(
                'SPLITIO.split.sample_feature',
                'SPLITIO.splits.till',
                'SPLITIO.split.all_feature',
                'SPLITIO.split.killed_feature',
                'SPLITIO.split.Risk_Max_Deductible',
                'SPLITIO.split.whitelist_feature',
                'SPLITIO.split.regex_test',
                'SPLITIO.split.boolean_test',
                'SPLITIO.split.dependency_test'
            )

class SegmentStorageTests(object):
    """Redis Segment storage e2e tests."""

    def test_put_fetch_contains(self):
        """Test storing and retrieving splits in redis."""
        adapter = _build_default_client({})
        try:
            storage = RedisSegmentStorage(adapter)
            adapter.sadd(storage._get_key('some_segment'), 'key1', 'key2', 'key3', 'key4')
            adapter.set(storage._get_till_key('some_segment'), 123)
            assert storage.segment_contains('some_segment', 'key0') is False
            assert storage.segment_contains('some_segment', 'key1') is True
            assert storage.segment_contains('some_segment', 'key2') is True
            assert storage.segment_contains('some_segment', 'key3') is True
            assert storage.segment_contains('some_segment', 'key4') is True
            assert storage.segment_contains('some_segment', 'key5') is False

            fetched = storage.get('some_segment')
            assert fetched.keys == set(['key1', 'key2', 'key3', 'key4'])
            assert fetched.change_number == 123
        finally:
            adapter.delete('SPLITIO.segment.some_segment', 'SPLITIO.segment.some_segment.till')


class ImpressionsStorageTests(object):
    """Redis Impressions storage e2e tests."""

    def test_put_fetch_contains(self):
        """Test storing and retrieving splits in redis."""
        adapter = _build_default_client({})
        try:
            metadata = get_metadata()
            storage = RedisImpressionsStorage(adapter, metadata)
            storage.put([
                impressions.Impression('key1', 'feature1', 'on', 'l1', 123456, 'b1', 321654),
                impressions.Impression('key2', 'feature1', 'on', 'l1', 123456, 'b1', 321654),
                impressions.Impression('key3', 'feature1', 'on', 'l1', 123456, 'b1', 321654)
            ])

            imps = adapter.lrange('SPLITIO.impressions', 0, 2)
            assert len(imps) == 3
        finally:
            adapter.delete('SPLITIO.impressions')


class EventsStorageTests(object):
    """Redis Events storage e2e tests."""

    def test_put_fetch_contains(self):
        """Test storing and retrieving splits in redis."""
        adapter = _build_default_client({})
        try:
            metadata = get_metadata()
            storage = RedisEventsStorage(adapter, metadata)
            storage.put([
                events.Event('key1', 'user', 'purchase', 3.5, 123456),
                events.Event('key2', 'user', 'purchase', 3.5, 123456),
                events.Event('key3', 'user', 'purchase', 3.5, 123456)
            ])

            evts = adapter.lrange('SPLITIO.events', 0, 2)
            assert len(evts) == 3
        finally:
            adapter.delete('SPLITIO.events')


class TelemetryStorageTests(object):
    """Redis Telemetry storage e2e tests."""

    def test_put_fetch_contains(self):
        """Test storing and retrieving splits in redis."""
        adapter = _build_default_client({})
        metadata = get_metadata()
        storage = RedisTelemetryStorage(adapter, metadata)
        try:

            storage.inc_counter('counter1')
            storage.inc_counter('counter1')
            storage.inc_counter('counter2')
            assert adapter.get(storage._get_counter_key('counter1')) == '2'
            assert adapter.get(storage._get_counter_key('counter2')) == '1'

            storage.inc_latency('latency1', 3)
            storage.inc_latency('latency1', 3)
            storage.inc_latency('latency2', 6)
            assert adapter.get(storage._get_latency_key('latency1', 3)) == '2'
            assert adapter.get(storage._get_latency_key('latency2', 6)) == '1'

            storage.put_gauge('gauge1', 3)
            storage.put_gauge('gauge2', 1)
            assert adapter.get(storage._get_gauge_key('gauge1')) == '3'
            assert adapter.get(storage._get_gauge_key('gauge2')) == '1'

        finally:
            adapter.delete(
                storage._get_counter_key('counter1'),
                storage._get_counter_key('counter2'),
                storage._get_latency_key('latency1', 3),
                storage._get_latency_key('latency2', 6),
                storage._get_gauge_key('gauge1'),
                storage._get_gauge_key('gauge2')
            )