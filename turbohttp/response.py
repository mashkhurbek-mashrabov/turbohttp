import json
from webob import Response as WobResponse


class Response:
    def __init__(self, *args, **kwargs):
        self.json = None
        self.html = None
        self.text = None
        self.content_type = None
        self.body = b''
        self.status_code = 200

    def __call__(self, environ, start_response):
        self._set_body_and_content_type()
        response = WobResponse(
            body=self.body,
            status=self.status_code,
            content_type=self.content_type
        )
        return response(environ, start_response)

    def _set_body_and_content_type(self):
        if self.json is not None:
            self.body = json.dumps(self.json).encode()
            self.content_type = 'application/json'

        elif self.html is not None:
            self.body = self.html.encode()
            self.content_type = 'text/html'

        elif self.text is not None:
            self.body = self.text
            self.content_type = 'text/plain'
