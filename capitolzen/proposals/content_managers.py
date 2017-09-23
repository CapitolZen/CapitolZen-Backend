import magic
import requests
from rest_framework import status


class ContentManager(object):
    # TODO implement something like bag-of-words / scikit to determine if page
    # is actually a bill or not
    url = None
    response = None
    headers = None
    file_type = None
    encoding = None
    text = None
    content_type = None
    json = None

    _gathered_content = False

    def __init__(self, url):
        self.url = url

    def _get_file_type(self):
        response = self.get_content()
        if response is None:
            self.file_type = None
        if self.content_type is None:
            # get file type by file extension
            pass

    def _is_bill_text(self):
        # Determine if the file / page contains the actual bill text
        # or if we need to scrounge around to find what looks like a
        # bill
        pass

    def get_content(self):
        if self._gathered_content or self._gathered_content is None:
            return self.response
        self.response = requests.get(self.url)
        if self.response.status_code == status.HTTP_200_OK:
            self._gathered_content = True
            self.response = self.response
            self.headers = self.response.headers
            self.encoding = self.response.encoding
            self.text = self.response.text
            self.content_type = self.headers.get(
                'content-type', self.headers.get('Content-Type'))
            if "application/json" in self.content_type:
                try:
                    self.json = self.response.json()
                except ValueError:
                    self.json = None
        else:
            self._gathered_content = None
        return self.response

    def parse_content(self):
        pass


class BillManager(ContentManager):
    pass
