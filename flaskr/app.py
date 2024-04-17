from flask import Flask, request, render_template, send_file
from lib.annotate import AnnotatedPDFGenerator, LayoutRule
import os

app = Flask(__name__)
print(os.getcwd())

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate', methods = ["POST"])
def generate_pdf():
    

    f = request.files["pdftoconvert"]
    f.save('C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\pdftoconvert.pdf')
    

    #Convertire il pdf
    generator: AnnotatedPDFGenerator = AnnotatedPDFGenerator(
        input_fp='C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\pdftoconvert.pdf', output_fp='C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\pdfconverted.pdf', layout=LayoutRule.GRID
    )

    generator.run()

    return send_file('C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\pdfconverted.pdf', as_attachment=True)

if __name__ == "__main__":
    app.run(debug = True)
