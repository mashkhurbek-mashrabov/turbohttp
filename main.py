from app import TurboHTTP

app = TurboHTTP()


@app.route("/", methods=["GET"])
def home(request, response):
    response.text = "Hello, World!"
    return response


@app.route("/about")
def about(request, response):
    response.text = "About Page"
    return response


@app.route("/hello/{name}")
def hello(request, response, name):
    response.text = f"Hello, {name}!"
    return response


@app.route("/books")
class Books:
    def get(self, request, response):
        response.text = "Books Page"

    def post(self, request, response):
        response.text = "Books Post Page"


def new_handler(request, response):
    response.text = "From New Handler"


@app.route("/template")
def template_handler(request, response):
    response.body = app.template("home.html",
                                 context={"title": "New Title", 'body': "New Body"})


@app.route("/exception")
def exception_handler(request, response):
    raise Exception("Something went wrong")


def on_exception(request, response, exception):
    response.text = str(exception)


app.add_exception_handler(on_exception)
app.add_route("/new", new_handler)
