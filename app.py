from webob import Request, Response


class TurboHTTP:
    def __call__(self, environ, start_response, *args, **kwargs):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        user_agent = request.headers.get('User-Agent', "Unknown")
        response = Response()
        response.status_code = 200
        response.text = f'Hello, {user_agent}!'
        return response
