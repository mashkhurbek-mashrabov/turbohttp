import pytest


def test_basic_route_adding(app):
    @app.route("/")
    def index(request, response):
        response.text = "Hello, World!"


def test_duplicate_route_adding(app):
    @app.route("/")
    def index(request, response):
        response.text = "Hello, World!"

    with pytest.raises(ValueError):
        @app.route("/")
        def index(request, response):
            response.text = "Hello, World!"


def test_request_can_be_sent_by_test_client(app, test_client):
    @app.route("/")
    def index(request, response):
        response.text = "Hello, World!"

    response = test_client.get("http://testserver")
    assert response.text == "Hello, World!"


def test_parameterize_route(app, test_client):
    @app.route("/hello/{name}")
    def hello(request, response, name):
        response.text = f"Hello, {name}!"

    response = test_client.get("http://testserver/hello/John")
    assert response.text == "Hello, John!"

    response = test_client.get("http://testserver/hello/Jane")
    assert response.text == "Hello, Jane!"


def test_default_response(app, test_client):
    response = test_client.get("http://testserver/nonexistent")
    assert response.status_code == 404
    assert response.text == "Not Found"


def test_class_based_get(app, test_client):
    @app.route("/books")
    class Books:
        def get(self, request, response):
            response.text = "Books Page"

    response = test_client.get("http://testserver/books")
    assert response.text == "Books Page"


def test_class_based_post(app, test_client):
    @app.route("/books")
    class Books:
        def post(self, request, response):
            response.text = "Books Post Page"

    response = test_client.post("http://testserver/books")
    assert response.text == "Books Post Page"


def test_class_based_get_and_post(app, test_client):
    @app.route("/books")
    class Books:
        def get(self, request, response):
            response.text = "Books Page"

        def post(self, request, response):
            response.text = "Books Post Page"

    response = test_client.get("http://testserver/books")
    assert response.text == "Books Page"

    response = test_client.post("http://testserver/books")
    assert response.text == "Books Post Page"


def test_class_based_not_allowed(app, test_client):
    @app.route("/books")
    class Books:
        def post(self, request, response):
            response.text = "Books Page"

    response = test_client.get("http://testserver/books")
    assert response.text == "Method Not Allowed"
    assert response.status_code == 405
