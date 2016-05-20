import pytest


def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': ':memory:'}},
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE_CLASSES=(
        ),
        INSTALLED_APPS=(
            'tests',
        ),
        AZURE_STORAGE={
            'CONTAINER': 'test-container',
            'ACCOUNT_NAME': 'test-name',
            'ACCOUNT_KEY': 'test-key',
        },
    )

@pytest.fixture
def default_storage(mock_service):
    from azure_storage.storage import AzureStorage

    storage = AzureStorage()
    storage._blob_service = mock_service

    return storage

@pytest.fixture
def mock_service():
    from mock import Mock

    service = Mock()

    def make_blob_url(*args, **kwargs):
        print(service)
        print(service.called)

        return 'http://{host}/{container}/{blob}'.format(
            host=kwargs.get('host_base', 'test-name.blob.core.windows.net'),
            container=kwargs['container_name'],
            blob=kwargs['blob_name'],
        )

    service.make_blob_url = make_blob_url

    return service
