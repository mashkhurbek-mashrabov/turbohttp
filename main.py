from app import TurboHTTP

app = TurboHTTP()


@app.route("/")
def home(request, response):
    response.text = "Hello, World!"
    return response


@app.route("/about")
def about(request, response):
    response.text = "About Page"
    return response
