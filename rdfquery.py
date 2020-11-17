import rdflib
from gtts import gTTS
from googletrans import Translator
from googletrans import constants
import os
import time
import playsound
import speech_recognition as sr


translator = Translator(service_urls=constants.DEFAULT_SERVICE_URLS)
g = rdflib.Graph()
g.parse("db.rdf")


def speak(text):
    tts = gTTS(text=text, lang='it')
    filename = 'voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)


def getAudio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio, language='it-IT')
            print(said)
        except Exception as e:
            print("Exception: " + str(e))
    return said


# Questa funzione restituisce il numero di pubblicazioni relative alla nazione che riceve come parametro
def pubblicazioni_per_nazione(stringname):
    enStr = translator.translate(stringname, dest='en')
    sparql = '''PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
                SELECT ?json_data_num_publications
                WHERE 
                {
                    ?json_data_primaryId db:json_data_name ?json_data_name .
                    ?json_data_primaryId db:json_data_type ?json_data_type .
                    ?json_data_primaryId db:json_data_num_publications ?json_data_num_publications .
                    FILTER (regex(?json_data_type, "country")) .
                    FILTER (regex(?json_data_name, "''' + enStr.text + '''"))
                }       
                '''
    response = g.query(sparql)
    total = 0
    for row in response:
        total += int(row.asdict()['json_data_num_publications'].toPython())

    if total != 0:
        return 'Il numero di pubblicazioni in ' + stringname.capitalize() + ' è ' + str(total)
    else:
        return 'La query non ha restituito nessun risultato'


def maggior_pubblicazioni(stringtype):
    if stringtype == 'nazione':
        stringtype = 'paese'
    if stringtype == 'rivista':
        stringtype = 'journal'

    enStr = translator.translate(stringtype, dest='en')

    sparql = '''PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
                SELECT ?json_data_name ?json_data_type (SUM(xsd:integer(?json_data_num_publications)) AS ?tot)
                WHERE 
                {
                    ?json_data_primaryId db:json_data_name ?json_data_name .
                    ?json_data_primaryId db:json_data_type ?json_data_type .
                    ?json_data_primaryId db:json_data_num_publications ?json_data_num_publications .
                    ?json_data_primaryId db:json_data_num_citations ?json_data_num_citations  
                    FILTER( regex(?json_data_type, "''' + enStr.text + '''") )
                }
                GROUP BY ?json_data_name
                ORDER BY DESC(?tot) LIMIT 1                       
            '''
    fraseDaDire = 'Scusa, non so rispondere a questa domanda'
    response = g.query(sparql)
    string = ''
    number = ''
    for row in response:
        string = row.asdict()['json_data_name'].toPython()
        number = row.asdict()['tot'].toPython()
    if stringtype.capitalize() == 'Autore':
        fraseDaDire = "L'autore che ha pubblicato di più è " + string + " con ben " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Conferenza':
        fraseDaDire = "La conferenza con più pubblicazioni è " + string + " con ben " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Paese':
        fraseDaDire = "Il paese con più pubblicazioni è " + string + " con ben " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Istituzione':
        fraseDaDire = "L'istituzione con più pubblicazioni è " + string + " con ben " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Journal':
        fraseDaDire = "La rivista che ha pubblicato di più è " + string + " con ben " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Topic':
        fraseDaDire = "Il topic con più pubblicazioni è " + string + " con ben " + str(number) + " pubblicazioni"
    speak(fraseDaDire)


def minor_pubblicazioni(stringtype):
    if stringtype == 'nazione':
        stringtype = 'paese'
    if stringtype == 'rivista':
        stringtype = 'journal'
    enStr = translator.translate(stringtype, dest='en')

    sparql = '''PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
                SELECT ?json_data_name ?json_data_type (SUM(xsd:integer(?json_data_num_publications)) AS ?tot)
                WHERE 
                {
                    ?json_data_primaryId db:json_data_name ?json_data_name .
                    ?json_data_primaryId db:json_data_type ?json_data_type .
                    ?json_data_primaryId db:json_data_num_publications ?json_data_num_publications .
                    ?json_data_primaryId db:json_data_num_citations ?json_data_num_citations  
                    FILTER( regex(?json_data_type, "''' + enStr.text + '''") )
                }
                GROUP BY ?json_data_name
                ORDER BY ASC(?tot) LIMIT 1                       
            '''
    response = g.query(sparql)
    fraseDaDire = 'Scusa, non so rispondere a questa domanda'
    string = ''
    number = ''
    for row in response:
        string = row.asdict()['json_data_name'].toPython()
        number = row.asdict()['tot'].toPython()
    if stringtype.capitalize() == 'Autore':
        fraseDaDire = "L'autore che ha pubblicato di meno è " + string + " con sole " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Conferenza':
        fraseDaDire = "La conferenza con meno pubblicazioni è " + string + " con sole " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Paese':
        fraseDaDire = "Il paese con meno pubblicazioni è " + string + " con sole " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Istituzione':
        fraseDaDire = "L'istituzione con meno pubblicazioni è " + string + " con sole " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Journal':
        fraseDaDire = "La rivista che ha pubblicato di meno è " + string + " con sole " + str(number) + " pubblicazioni"
    if stringtype.capitalize() == 'Topic':
        fraseDaDire = "Il topic con meno pubblicazioni è " + string + " con sole " + str(number) + " pubblicazioni"
    speak(fraseDaDire)


# ---------------------Inizio Script------------------------------------
speak("Ciao, sono Scholarly Data! Fammi una domanda!")
risp = 'sì'
first = True
while risp.__contains__('sì'):
    if not first:
        speak("Ok, fammi una domanda!")
    first = False
    query = getAudio()

    if query.__contains__('Quante pubblicazioni ci sono state in '):
        result = pubblicazioni_per_nazione((query.split(' ')[6]).split('?')[0])
        speak(result)
    else:
        if query.__contains__('ha pubblicato di più'):
            maggior_pubblicazioni(query.split(' ')[1])
        else:
            if query.__contains__('ha pubblicato di meno'):
                minor_pubblicazioni(query.split(' ')[1])
            else:
                speak("Scusa, non so rispondere a questa domanda.")

    speak("Vuoi farmi un'altra domanda?")
    risp = getAudio()

speak('Ok, alla prossima ricerca! Ciao!')
