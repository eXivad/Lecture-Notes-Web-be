from flask import Flask, request, render_template, send_file, redirect
from lib.annotate import AnnotatedPDFGenerator, LayoutRule
import os
import threading

app = Flask(__name__)
print(os.getcwd())

def get_thread_state(thread_name):
    for thread in threading.enumerate():
        if thread.name == thread_name:
            return thread.is_alive()

    return False

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/generate', methods = ["POST"])
def generate_pdf():

    f = request.files["pdftoconvert"] #Salvo il File ricevuto dal Form

    #Calcolo l'hash del file per utilizzare una chiave univoca sia per il nome del file che per la sessione di download
    file_id: int = hash(f) 

    #Salvo il file per la conversione
    f.save(f'C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\{file_id}.pdf')
    
    #Impostazione Generatore
    generator: AnnotatedPDFGenerator = AnnotatedPDFGenerator(
        input_fp=f'C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\{file_id}.pdf', output_fp='C:\\Users\\david\\Desktop\\Code\\Lecture-Notes-Web\\flaskr\\temp\\{file_id}_gen.pdf', layout=LayoutRule.GRID
    )
    
    #Avvio Conversione in nuovo Thread
    new_generation = threading.Thread(target=generator.run, name = file_id)
    new_generation.start()

    return redirect(f'/download/{file_id}')

#Route di download file che permette di sapere al client quando il suo file e pronto
@app.route('/download/<file_id>')
def download(file_id):
    get_thread_state(file_id)
    pass

#Una volta che il file è stato scaricato eliminarlo dal server per salvare spazio

if __name__ == "__main__":
    app.run(debug = True)
