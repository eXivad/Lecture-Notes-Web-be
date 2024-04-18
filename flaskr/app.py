from flask import Flask, request, render_template, send_file, redirect, session
from lib.annotate import AnnotatedPDFGenerator, LayoutRule
from flask_socketio import SocketIO
import os
import threading
import secrets

UPLOAD_FOLDER = "/temp"

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = secrets.token_hex()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

#Home route
@app.route('/')
def home():
    return render_template("index.html")

#API per generare il file pdf
def generate_and_notify(generator: AnnotatedPDFGenerator):
    generator.start()
    generator.join()
    socketio.emit('pdf_ready', {'file': 'done'})

@app.route('/generate', methods = ["POST"])
def generate_pdf():

    #Salvo il File ricevuto dal Form
    f = request.files["pdftoconvert"]
    layout: LayoutRule = LayoutRule(request.form['paper_type'])

    #Calcolo l'hash del file per utilizzare una chiave univoca sia per il nome del file che per la sessione di download
    file_id: int = hash(f)

    #Salvo il file per la conversione
    f.save(f'C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\{file_id}.pdf')

    #Avvio Conversione in nuovo Thread
    generator: AnnotatedPDFGenerator = AnnotatedPDFGenerator(
        input_fp=f'C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\{file_id}.pdf', output_fp=f'C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\{file_id}_gen.pdf', layout=layout
    )

    thread = threading.Thread(target = generate_and_notify, args=[generator])
    thread.start()

    return redirect(f'/download/{file_id}/page')

#Route di download file che permette di sapere al client quando il suo file e pronto

@app.route('/download/<file_id>')
def download(file_id):
    return send_file(f'C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\{file_id}_gen.pdf')

@app.route('/download/<file_id>/page')
def download_page(file_id):
    return render_template("download.html", id=file_id)

if __name__ == "__main__":
    socketio.run(app)

