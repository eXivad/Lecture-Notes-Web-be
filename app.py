import os
from flask import Flask, request, render_template, send_file, url_for
from lib.annotate import AnnotatedPDFGenerator, LayoutRule

upload_folder = os.path.join(os.getcwd(), 'temp')

app = Flask(__name__)
app.debug = True

#Home route
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate', methods = ["POST"])
def generate_pdf():

    #Salvo il File ricevuto dal Form
    f = request.files["pdftoconvert"]
    layout: LayoutRule = LayoutRule(request.form['paper_type'])

    #Calcolo l'hash del file per utilizzare una chiave univoca sia per il nome del file che per la sessione di download
    file_id: str = str(hash(f))

    #Salvo il file per la conversione
    f.save(os.path.join(upload_folder, file_id+'.pdf'))

    #Avvio Conversione
    generator: AnnotatedPDFGenerator = AnnotatedPDFGenerator(
        input_fp=os.path.join(upload_folder, file_id+'.pdf'), 
        output_fp=os.path.join(upload_folder, file_id+'_gen.pdf'), 
        layout=layout
    )

    generator.run()

    return {'download_link': f'{url_for('download', file_id = file_id)}'}


#API Download Generated PDF and Delete them
@app.route('/download/<file_id>')
def download(file_id):

    response = send_file(os.path.join(upload_folder, file_id+'_gen.pdf'), as_attachment=True)
    os.remove(os.path.join(upload_folder, file_id+'.pdf'))
    os.remove(os.path.join(upload_folder, file_id+'_gen.pdf'))

    return response

'''
@app.route('/download/page/<file_id>')
def download_page(file_id):
    return render_template("download.html", id=file_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

'''