from azure import WindowsAzureMissingResourceError
from azure.storage import BlobService

from django.core.files.storage import Storage
from django.conf import settings

try:
    from django.utils.deconstruct import deconstructible
except ImportError:
    # Support for django 1.7 and below
    def deconstructible(func):
        return func


@deconstructible
class AzureStorage(Storage):
    """
    Custom file storage system for Azure
    """

    container = settings.AZURE_STORAGE['CONTAINER']
    account_name = settings.AZURE_STORAGE['ACCOUNT_NAME']
    account_key = settings.AZURE_STORAGE['ACCOUNT_KEY']
    cdn_host = None
    use_ssl = settings.AZURE_STORAGE['USE_SSL']

    def __init__(self, account_name=None, account_key=None, container=None,
         use_ssl=None):

        if account_name is not None:
            self.account_name = account_name

        if account_key is not None:
            self.account_key = account_key

        if container is not None:
            self.container = container

        if use_ssl is not None:
            self.use_ssl = use_ssl

    def __getstate__(self):
        return dict(account_name=self.account_name,
            account_key=self.account_key, container=self.container,
            cdn_host=self.cdn_host, use_ssl=self.use_ssl)

    def _get_protocol(self):
        if self.use_ssl:
            return 'https'

        return 'http'

    def _get_service(self):
        if not hasattr(self, '_blob_service'):
            self._blob_service = BlobService(account_name=self.account_name,
                account_key=self.account_key, protocol=self._get_protocol())

        return self._blob_service

    def _get_container_url(self):
        if self.cdn_host is not None:
            return self.cdn_host

        if not hasattr(self, '_container_url'):
            self._container_url = '%s://%s/%s' % (self._get_protocol(),
                self._get_service()._get_host(), self.container)

        return self._container_url

    def _get_properties(self, name):
        return self._get_service().get_blob_properties(self.container,
                name)

    def _get_file_obj(self, name):
        """
        Helper function to get retrieve the requested Cloud Files Object.
        """
        return self._get_service().get_blob(self.container, name)

    def _open(self, name, mode='rb'):
        """
        Return the AzureStorageFile.
        """

        from django.core.files.base import ContentFile

        contents = self._get_service().get_blob(self.container, name)

        return ContentFile(contents)

    def _save(self, name, content):
        """
        Use the Azure Storage service to write ``content`` to a remote file
        (called ``name``).
        """
        import mimetypes

        content.open()

        content_type = None

        if hasattr(content.file, 'content_type'):
            content_type = content.file.content_type
        else:
            content_type = mimetypes.guess_type(name)[0]

        content_str = content.read()

        cache_control = self.get_cache_control(self.container, name,
                                               content_type)

        self._get_service().put_blob(self.container, name, content_str,
                                     x_ms_blob_type="BlockBlob",
                                     x_ms_blob_content_type=content_type,
                                     cache_control=cache_control,
                                     x_ms_blob_cache_control=cache_control)

        content.close()

        return name

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """

        files = []

        if path and not path.endswith('/'):
            path = '%s/' % path

        path_len = len(path)

        blob_list = self._get_service().list_blobs(self.container, prefix=path)

        for name in blob_list:
            files.append(name[path_len:])

        return ([], files)

    def exists(self, name):
        """
        Returns True if a file referenced by the given name already exists in
        the storage system, or False if the name is available for a new file.
        """
        try:
            self._get_properties(name)

            return True
        except WindowsAzureMissingResourceError:
            return False

    def delete(self, name):
        """
        Deletes the file referenced by name.
        """

        try:
            self._get_service().delete_blob(self.container, name)
        except WindowsAzureMissingResourceError:
            pass

    def get_cache_control(self, container, name, content_type):
        """
        Get the Cache-Control value for a blob, used when saving the blob on
        Azure.  Returns `None` by default to remain compatible with the
        default setting for the SDK.
        """

        return None

    def size(self, name):
        """
        Returns the total size, in bytes, of the file referenced by name.
        """

        try:
            properties = self._get_properties(name)

            return int(properties['content-length'])
        except WindowsAzureMissingResourceError:
            pass

    def url(self, name):
        """
        Returns the URL where the contents of the file referenced by name can
        be accessed.
        """

        return '%s/%s' % (self._get_container_url(), name)

    def modified_time(self, name):
        """
        Returns a datetime object containing the last modified time.
        """

        import datetime

        try:
            properties = self._get_properties(name)

            return datetime.datetime.strptime(properties['last-modified'],
                '%a, %d %b %Y %H:%M:%S %Z')
        except WindowsAzureMissingResourceError:
            pass
