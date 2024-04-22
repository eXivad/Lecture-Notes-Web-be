import os
from flask import Flask, request, render_template, send_file, redirect
from lib.annotate import AnnotatedPDFGenerator, LayoutRule
from flask_socketio import SocketIO
import threading
import time

upload_folder = os.path.join(os.getcwd(), 'temp')

app = Flask(__name__)
socketio = SocketIO(app)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.debug = True

#Home route
@app.route('/')
def home():
    return render_template("index.html")

#API per generare il file pdf
def generate_and_notify(generator: AnnotatedPDFGenerator):
    generator.start()
    generator.join()
    emit_pdf_ready()

@app.route('/generate', methods = ["POST"])
def generate_pdf():

    #Salvo il File ricevuto dal Form
    f = request.files["pdftoconvert"]
    layout: LayoutRule = LayoutRule(request.form['paper_type'])

    #Calcolo l'hash del file per utilizzare una chiave univoca sia per il nome del file che per la sessione di download
    file_id: str = str(hash(f))

    #Salvo il file per la conversione
    f.save(os.path.join(upload_folder, file_id+'.pdf'))

    #Avvio Conversione in nuovo Thread
    generator: AnnotatedPDFGenerator = AnnotatedPDFGenerator(
        input_fp=os.path.join(upload_folder, file_id+'.pdf'), 
        output_fp=os.path.join(upload_folder, file_id+'_gen.pdf'), 
        layout=layout
    )

    thread = threading.Thread(target = generate_and_notify, args=[generator])
    thread.start()

    return redirect(f'/download/page/{file_id}')

#Route di download file che permette di sapere al client quando il suo file e pronto

@app.route('/download/<file_id>')
def download(file_id):
    threading.Thread(target=download_and_delete, args = [file_id]).start()
    return send_file(os.path.join(upload_folder, file_id+'_gen.pdf'), as_attachment=True)

@app.route('/download/page/<file_id>')
def download_page(file_id):
    if(os.path.exists(os.path.join(upload_folder, file_id+'_gen.pdf'))):
        threading.Thread(target=emit_pdf_ready, args=[3]).start()
    return render_template("download.html", id=file_id)

def download_and_delete(file_id):
    time.sleep(10)
    os.remove(os.path.join(upload_folder, file_id+'.pdf'))
    os.remove(os.path.join(upload_folder, file_id+'_gen.pdf'))

def emit_pdf_ready(time_sleep=0):
    time.sleep(time_sleep)
    socketio.emit('pdf_ready', {'file': 'done'})

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8000)

