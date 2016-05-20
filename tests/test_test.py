from azure_storage.storage import AzureStorage

from azure.common import AzureMissingResourceHttpError
from mock import Mock


def test_delete_exists(default_storage):
    delete_blob = Mock()
    default_storage._blob_service.delete_blob = delete_blob

    default_storage.delete('something')

    delete_blob.assert_called_with('test-container', 'something')

def test_delete_doesnt_exist(default_storage):
    delete_blob = Mock(
        side_effect=AzureMissingResourceHttpError('Missing', 404)
    )
    default_storage._blob_service.delete_blob = delete_blob

    default_storage.delete('something')

    delete_blob.assert_called_with('test-container', 'something')

def test_url(default_storage):
    url = default_storage.url('test')

    assert url == 'http://test-name.blob.core.windows.net/test-container/test'

def test_url_ssl(default_storage):
    default_storage.use_ssl = True
    url = default_storage.url('test')

    assert url == 'https://test-name.blob.core.windows.net/test-container/test'

def test_url_cdn(default_storage):
    default_storage.cdn_host = 'http://example.com/test-container'
    url = default_storage.url('test')

    assert url == 'http://example.com/test-container/test'

def test_url_cdn_no_container(default_storage):
    default_storage.cdn_host = 'http://example.com'
    url = default_storage.url('test')

    assert url == 'http://example.com/test'
