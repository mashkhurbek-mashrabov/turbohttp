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
    @app.route("/books", methods=["POST"])
    class Books:
        def post(self, request, response):
            response.text = "Books Post Page"

    response = test_client.post("http://testserver/books")
    assert response.status_code == 200
    assert response.text == "Books Post Page"


def test_class_based_get_and_post(app, test_client):
    @app.route("/books", methods=["GET", "POST"])
    class Books:
        def get(self, request, response):
            response.text = "Books Page"

        def post(self, request, response):
            response.text = "Books Post Page"

    response = test_client.get("http://testserver/books")
    assert response.status_code == 200
    assert response.text == "Books Page"

    response = test_client.post("http://testserver/books")
    assert response.status_code == 200
    assert response.text == "Books Post Page"


def test_class_based_not_allowed(app, test_client):
    @app.route("/books")
    class Books:
        def post(self, request, response):
            response.text = "Books Page"

    response = test_client.get("http://testserver/books")
    assert response.text == "Method Not Allowed"
    assert response.status_code == 405


def test_add_route(app, test_client):
    def new_handler(request, response):
        response.text = "From New Handler"

    app.add_route('/new', new_handler)

    response = test_client.get("http://testserver/new")
    assert response.text == "From New Handler"


def test_template_rendering(app, test_client):
    @app.route("/template")
    def template(request, response):
        response.body = app.template("home.html",
                                     context={"title": "Test Title", 'body': "Test Body"})

    response = test_client.get("http://testserver/template")
    assert "Test Title" in response.text
    assert "Test Body" in response.text
    assert "text/html" in response.headers["Content-Type"]


def test_custom_exception_handler(app, test_client):
    def on_exception(request, response, exception):
        response.text = "Something went wrong"

    app.add_exception_handler(on_exception)

    response = test_client.get("http://testserver/nonexistent")
    assert response.text == "Something went wrong"
