from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from flask import render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os


#to serve video
from flask import send_file




#for gcp
from google.cloud import storage

#for gcp speech
import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


#this part for categoriation of text
from collections import Counter
import math
import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import sys
from urllib.request import urlopen  

UPLOAD_FOLDER = 'sample_data/uploads'
bucket_name="my-xtra-cool-bucket"
destination_blob_name="sample_data"
gcs_uri="gs://my-xtra-cool-bucket/sample_data"


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def delete_file(filename):

    if os.path.isfile("/Users/amirulislam/Downloads/announce.wav"):
        os.remove("/Users/amirulislam/Downloads/announce.wav")    

    if os.path.isfile("/Users/amirulislam/Downloads/announce.txt"):
        os.remove("/Users/amirulislam/Downloads/announce.txt")


@app.route('/')
def hello():
    filename="announce.wav"
    # by default from the downloads folder
    delete_file(filename)
    return render_template('index.html')



#this function does the call to google to remotely convert the audio file to text

def transcribe_gcs(gcs_uri):
    """Transcribes the audio file specified by the gcs_uri."""
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code='en-US',
        audio_channel_count=2)


    response = client.recognize(config, audio)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))
        return result.alternatives[0].transcript


@app.route('/getvideo')

def download_video():
    try:
        return send_file('/Users/amirulislam/Downloads/k1.mp4', attachment_filename='k1.mp4')
    except Exception as e:
        return str(e)    



@app.route('/audio-file',methods=['POST'])
def get_audio():

    if request.method=="POST":

        print(request)
        
        file = request.files['myAudioFile']
        filename = secure_filename(file.filename)

        print(filename)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("filename is ",filename)
        dest=os.path.join(app.config['UPLOAD_FOLDER'], filename)

        print("dest file is ",dest)
        source_file_name=dest
        upload_blob(bucket_name, source_file_name, destination_blob_name)

        # return redirect(url_for('uploaded_file',filename=filename))
        text_transcribed=transcribe_gcs(gcs_uri)

        print("The transcription is ",text_transcribed)

        
        
        

    return text_transcribed

import wave


import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


def audio_to_text():
    # Instantiates a client
    client = speech.SpeechClient()
    file_name="/Users/amirulislam/Downloads/announce.wav"
    print("File is ",file_name)


    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code='ar-QA',
        audio_channel_count=1)

    # Detects speech in the audio file
    response = client.recognize(config, audio)

    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))   
    return  response.results[0].alternatives[0].transcript

from google.cloud import translate

def translate_string(arabic_string):
    # Imports the Google Cloud client library
    

    

    # Instantiates a client
    translate_client = translate.Client()

    # The text to translate
    text = arabic_string
    # The target language
    target = 'en'

    # Translates some text into Russian
    translation = translate_client.translate(
        text,
        target_language=target)

    print(u'Text: {}'.format(text))
    print(u'Translation: {}'.format(translation['translatedText']))
    return translation['translatedText']



import webbrowser




@app.route('/uploadajax',methods=['POST'])
def handle_uploaded_audio_file():
    print("in uploadajax")
    the_files=request.files
    file=the_files['audio_data']

    print(the_files['audio_data'])
    file.save("/Users/amirulislam/Downloads/announce.wav")

    announce_string=audio_to_text()

    print(announce_string)
    english_announcement_text=None
    if announce_string != None:
        english_announcement_text=translate_string(announce_string)

    print(english_announcement_text)
    f= open("/Users/amirulislam/Downloads/announce.txt","w+")
    f.write(english_announcement_text)
    f.close()
    
    val=vidplay()
    print("to send ",val)
    return val
    # return english_announcement_text
    # return render_template('vidplay.html')
    # return webbrowser.open_new_tab('https://192.168.0.109:5000/vidplay.html')


# def upload_to_gcloud(bucket_name, source_file, destination_blob_name):


def counter_cosine_similarity(c1, c2):

    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    return dotprod / (magA * magB)

import time
# @app.route('/vidplay')
def vidplay():
    time.sleep(0.5)
    while os.path.isfile("/Users/amirulislam/Downloads/announce.txt") == False:
        print("")
    f= open("/Users/amirulislam/Downloads/announce.txt","r+")
    contents =f.read()
    f.close()

    print(contents)



    rawData = str.lower(contents)

    tokens = nltk.word_tokenize(rawData)
    emergencyWords = ["fire","evacuation","urgent", "drill", "security","burn","terrorist",

                    "lockdown","explosion","weapon","blast", "bomb","emergency", "evacuate", "immediately", "leave",

                    "threat","alarm","fighting","alarm","security", "breach", "safety",

                    "danger", "safe"]

    stop_words = set(stopwords.words('english'))
    wordsFiltered = []

    for w in tokens:

        if w not in stop_words:

            wordsFiltered.append(w)

    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    counterA = Counter(emergencyWords)
    counterB = Counter(wordsFiltered)

    score = (counter_cosine_similarity(counterA, counterB) * 100)
    score2 = len(set(emergencyWords) & set(wordsFiltered))
    label = 0
    if score >= 10:
        label = 1


    print(rawData)
    print(label)
    baseURL = 'https://api.thingspeak.com/update?api_key=YMVZLJR0274N65RG&field1=0'
    f = urlopen(baseURL +str(label))
    f.read()
    f.close() 
    print("Message Category Sent")    

    if label == 1:        
        returnmsg={"message":"FireEvacuateBuilding"}
    elif label == 0:
        returnmsg={"message":"Planeleavesat9AM"}



    # return render_template('vidplay.html')
    return jsonify(returnmsg)



    


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))





if __name__ == "__main__":

    # app.run(debug=True,host='0.0.0.0',ssl_context='adhoc')
    app.run(debug=True,host='0.0.0.0')
