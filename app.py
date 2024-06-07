from parse import parse
from webob import Request, Response


class TurboHTTP:
    def __init__(self):
        self.routes = dict()

    def __call__(self, environ, start_response, *args, **kwargs):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request)
        if handler is not None:
            handler(request, response, **kwargs)
            response.status_code = 200
        else:
            response = self.default_response(response)

        return response

    def find_handler(self, request):
        for path, handler in self.routes.items():
            parsed_result = parse(path, request.path)
            if path == request.path or parsed_result is not None:
                return handler, parsed_result.named

        return None, None

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not Found"
        return response

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper
