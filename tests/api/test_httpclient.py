"""HTTPClient test module."""

from splitio.api import client

class HttpClientTests(object):
    """Http Client test cases."""

    def test_get(self, mocker):
        """Test HTTP GET verb requests."""
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.text = 'ok'
        get_mock = mocker.Mock()
        get_mock.return_value = response_mock
        mocker.patch('splitio.api.client.requests.get', new=get_mock)
        httpclient = client.HttpClient()
        response = httpclient.get('sdk', '/test1', 'some_api_key', {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            client.HttpClient.SDK_URL + '/test1',
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert response.status_code == 200
        assert response.body == 'ok'
        assert get_mock.mock_calls == [call]
        get_mock.reset_mock()

        response = httpclient.get('events', '/test1', 'some_api_key', {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            client.HttpClient.EVENTS_URL + '/test1',
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert get_mock.mock_calls == [call]
        assert response.status_code == 200
        assert response.body == 'ok'

    def test_get_custom_urls(self, mocker):
        """Test HTTP GET verb requests."""
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.text = 'ok'
        get_mock = mocker.Mock()
        get_mock.return_value = response_mock
        mocker.patch('splitio.api.client.requests.get', new=get_mock)
        httpclient = client.HttpClient(sdk_url='https://sdk.com', events_url='https://events.com')
        response = httpclient.get('sdk', '/test1', 'some_api_key', {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            'https://sdk.com/test1',
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert get_mock.mock_calls == [call]
        assert response.status_code == 200
        assert response.body == 'ok'
        get_mock.reset_mock()

        response = httpclient.get('events', '/test1', 'some_api_key', {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            'https://events.com/test1',
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert response.status_code == 200
        assert response.body == 'ok'
        assert get_mock.mock_calls == [call]


    def test_post(self, mocker):
        """Test HTTP GET verb requests."""
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.text = 'ok'
        get_mock = mocker.Mock()
        get_mock.return_value = response_mock
        mocker.patch('splitio.api.client.requests.post', new=get_mock)
        httpclient = client.HttpClient()
        response = httpclient.post('sdk', '/test1', 'some_api_key', {'p1': 'a'}, {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            client.HttpClient.SDK_URL + '/test1',
            json={'p1': 'a'},
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert response.status_code == 200
        assert response.body == 'ok'
        assert get_mock.mock_calls == [call]
        get_mock.reset_mock()

        response = httpclient.post('events', '/test1', 'some_api_key', {'p1': 'a'}, {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            client.HttpClient.EVENTS_URL + '/test1',
            json={'p1': 'a'},
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert response.status_code == 200
        assert response.body == 'ok'
        assert get_mock.mock_calls == [call]

    def test_post_custom_urls(self, mocker):
        """Test HTTP GET verb requests."""
        response_mock = mocker.Mock()
        response_mock.status_code = 200
        response_mock.text = 'ok'
        get_mock = mocker.Mock()
        get_mock.return_value = response_mock
        mocker.patch('splitio.api.client.requests.post', new=get_mock)
        httpclient = client.HttpClient(sdk_url='https://sdk.com', events_url='https://events.com')
        response = httpclient.post('sdk', '/test1', 'some_api_key', {'p1': 'a'}, {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            'https://sdk.com' + '/test1',
            json={'p1': 'a'},
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert response.status_code == 200
        assert response.body == 'ok'
        assert get_mock.mock_calls == [call]
        get_mock.reset_mock()

        response = httpclient.post('events', '/test1', 'some_api_key', {'p1': 'a'}, {'param1': 123}, {'h1': 'abc'})
        call = mocker.call(
            'https://events.com' + '/test1',
            json={'p1': 'a'},
            headers={'Authorization': 'Bearer some_api_key', 'h1': 'abc', 'Content-Type': 'application/json'},
            params={'param1': 123},
            timeout=None
        )
        assert response.status_code == 200
        assert response.body == 'ok'
        assert get_mock.mock_calls == [call]
