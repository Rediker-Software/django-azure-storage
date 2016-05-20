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
    make_blob_url = Mock(
        return_value='http://test-name.blob.core.windows.net/test-container/t'
    )
    default_storage._blob_service.make_blob_url = make_blob_url
    url = default_storage.url('t')

    assert url == 'http://test-name.blob.core.windows.net/test-container/t'

    make_blob_url.assert_called_with(
        container_name='test-container',
        blob_name='t',
    )

def test_url_cdn(default_storage):
    make_blob_url = Mock(
        return_value='http://example.com/test-container/test'
    )
    default_storage._blob_service.make_blob_url = make_blob_url
    default_storage.cdn_host = 'example.com'

    url = default_storage.url('test')

    assert url == 'http://example.com/test-container/test'

    make_blob_url.assert_called_with(
        container_name='test-container',
        blob_name='test',
        account_name='',
        host_base='example.com',
    )
