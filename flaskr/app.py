from flask import Flask, request, render_template, send_file

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate', methods = ["POST"])
def generate_pdf():
    f = request.files["pdftoconvert"]
    f.save("./temp/pdftoconvert.pdf")
    return send_file("./temp/pdftoconvert.pdf", as_attachment=True)
