from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def hello_world():
    name = request.args.get("name", "World")
    return f"Hello, {name}!"
