import inspect
import requests
import wsgiadapter
from parse import parse
from webob import Request, Response


class TurboHTTP:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()
        handler, allowed_methods, kwargs = self.find_handler(request)

        if handler:
            if request.method in allowed_methods:
                self.execute_handler(handler, request, response, **kwargs)
            else:
                self.method_not_allowed_response(response)
        else:
            self.default_response(response)

        return response

    def find_handler(self, request):
        for path, (handler, allowed_methods) in self.routes.items():
            parsed_result = parse(path, request.path)
            if path == request.path or parsed_result:
                return handler, allowed_methods, (parsed_result.named if parsed_result else {})
        return None, [], {}

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not Found"
        return response

    def execute_handler(self, handler, request, response, **kwargs):
        if inspect.isclass(handler):
            handler_instance = handler()
            method_name = request.method.lower()
            handler_method = getattr(handler_instance, method_name, None)
            if handler_method:
                handler_method(request, response, **kwargs)
            else:
                return self.method_not_allowed_response(response)
        else:
            handler(request, response, **kwargs)

        response.status_code = 200

    def method_not_allowed_response(self, response):
        response.status_code = 405
        response.text = "Method Not Allowed"

    def add_route(self, path, handler, methods=None):
        if methods is None:
            methods = ['GET']

        methods = [method.upper() for method in methods]
        self.routes[path] = (handler, methods)

    def route(self, path, methods=None):
        if path in self.routes:
            raise ValueError(f"Route already exists: {path}")

        if methods is None:
            methods = ['GET']

        methods = [method.upper() for method in methods]

        def wrapper(handler):
            self.routes[path] = (handler, methods)
            return handler

        return wrapper

    def test_session(self):
        session = requests.Session()
        session.mount("http://testserver", wsgiadapter.WSGIAdapter(self))
        return session
