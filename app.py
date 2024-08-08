import os
import inspect
import requests
import wsgiadapter
from whitenoise import WhiteNoise
from parse import parse
from webob import Request
from response import Response
from jinja2 import Environment, FileSystemLoader
from middleware import Middleware


class TurboHTTP:
    def __init__(self, template_dir="templates", static_dir="static", static_prefix="/static"):
        self.routes = {}
        self.exception_handler = None
        self.static_prefix = static_prefix

        loader = FileSystemLoader(os.path.abspath(template_dir))
        self.jinja_env = Environment(loader=loader)

        self.whitenoise = WhiteNoise(self.wsgi_app, root=os.path.abspath(static_dir), prefix=static_prefix)

        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.static_prefix):
            return self.whitenoise(environ, start_response)
        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()
        handler, allowed_methods, kwargs = self.find_handler(request)

        if handler:
            if request.method in allowed_methods:
                self.execute_handler(handler, request, response, allowed_methods, **kwargs)
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

    def execute_handler(self, handler, request, response, allowed_methods=None, **kwargs):
        if inspect.isclass(handler):
            method_name = request.method.lower()
            handler_instance = handler()
            handler_method = getattr(handler_instance, method_name, None)
            if handler_method:
                try:
                    handler_method(request, response, **kwargs)
                except Exception as e:
                    if self.exception_handler:
                        self.exception_handler(request, response, e)
                    else:
                        raise e
            else:
                return self.method_not_allowed_response(response)
        else:
            try:
                if request.method.upper() in allowed_methods:
                    handler(request, response, **kwargs)
                else:
                    self.method_not_allowed_response(response)
            except Exception as e:
                if self.exception_handler:
                    self.exception_handler(request, response, e)
                else:
                    raise e

        response.status_code = 200

    def method_not_allowed_response(self, response):
        response.status_code = 405
        response.text = "Method Not Allowed"

    def add_route(self, path, handler, methods=None):
        if path in self.routes:
            raise ValueError(f"Route already exists: {path}")

        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD', 'CONNECT', 'TRACE']

        methods = [method.upper() for method in methods]
        self.routes[path] = (handler, methods)

    def route(self, path, methods=None):
        def wrapper(handler):
            self.add_route(path, handler, methods)
            return handler

        return wrapper

    def test_session(self):
        session = requests.Session()
        session.mount("http://testserver", wsgiadapter.WSGIAdapter(self))
        return session

    def template(self, template_name, context: dict = None):
        if context is None:
            context = {}
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    def add_exception_handler(self, handler):
        self.exception_handler = handler

    def add_middleware(self, middleware):
        self.middleware.add(middleware)
