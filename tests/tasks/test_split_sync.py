"""Split syncrhonization task test module."""

import threading
import time
from splitio.api import APIException
from splitio.tasks import split_sync
from splitio.storage import SplitStorage
from splitio.models.splits import Split


class SplitSynchronizationTests(object):
    """Split synchronization task test cases."""

    def test_normal_operation(self, mocker):
        """Test the normal operation flow."""
        storage = mocker.Mock(spec=SplitStorage)
        def change_number_mock():
            change_number_mock._calls += 1
            if change_number_mock._calls == 1:
                return -1
            return 123
        change_number_mock._calls = 0
        storage.get_change_number.side_effect = change_number_mock

        api = mocker.Mock()
        splits =  [{
           'changeNumber': 123,
           'trafficTypeName': 'user',
           'name': 'some_name',
           'trafficAllocation': 100,
           'trafficAllocationSeed': 123456,
           'seed': 321654,
           'status': 'ACTIVE',
           'killed': False,
           'defaultTreatment': 'off',
           'algo': 2,
           'conditions': [
               {
                   'partitions': [
                       {'treatment': 'on', 'size': 50},
                       {'treatment': 'off', 'size': 50}
                   ],
                   'contitionType': 'WHITELIST',
                   'label': 'some_label',
                   'matcherGroup': {
                       'matchers': [
                           {
                               'matcherType': 'WHITELIST',
                               'whitelistMatcherData': {
                                   'whitelist': ['k1', 'k2', 'k3']
                               },
                               'negate': False,
                           }
                       ],
                       'combiner': 'AND'
                   }
               }
            ]
        }]

        def get_changes(*args, **kwargs):
            get_changes.called += 1

            if get_changes.called == 1:
                return {
                    'splits': splits,
                    'since': -1,
                    'till': 123
                }
            else:
                return {
                    'splits': [],
                    'since': 123,
                    'till': 123
                }
        get_changes.called = 0

        api.fetch_splits.side_effect = get_changes
        splits_ready_event = threading.Event()
        task = split_sync.SplitSynchronizationTask(api, storage, 1, splits_ready_event)
        task.start()
        splits_ready_event.wait(5)
        assert task.is_running()
        stop_event = threading.Event()
        task.stop(stop_event)
        stop_event.wait()
        assert splits_ready_event.is_set()
        assert not task.is_running()
        api_calls = api.fetch_splits.mock_calls
        assert mocker.call(-1) in api.fetch_splits.mock_calls
        assert mocker.call(123) in api.fetch_splits.mock_calls

        inserted_split = storage.put.mock_calls[0][1][0]
        assert isinstance(inserted_split, Split)
        assert inserted_split.name == 'some_name'

    def test_that_errors_dont_stop_task(self, mocker):
        """Test that if fetching splits fails at some_point, the task will continue running."""
        storage = mocker.Mock(spec=SplitStorage)
        api = mocker.Mock()
        def run(x):
            run._calls +=1
            if run._calls == 1:
                return {'splits': [], 'since': -1, 'till': -1}
            if run._calls == 2:
                return {'splits': [], 'since': -1, 'till': -1}
            raise APIException("something broke")
        run._calls = 0
        api.fetch_splits.side_effect = run
        storage.get_change_number.return_value = -1

        splits_ready_event = threading.Event()
        task = split_sync.SplitSynchronizationTask(api, storage, 0.5, splits_ready_event)
        task.start()
        splits_ready_event.wait(5)
        assert task.is_running()
        time.sleep(1)
        assert task.is_running()
        task.stop()
