from flask import Flask, render_template, request, send_from_directory
from moviepy.video.io.VideoFileClip import VideoFileClip
from deepgram import Deepgram
import requests
import openai
import random
import json
import math
import os


developement = True
if developement:
  from dotenv import load_dotenv
  load_dotenv()

edu_file = "educational_videos.txt" if not developement else "../educational_videos.txt"
with open(edu_file, "r", encoding="utf-8") as file:
    videos = file.read().splitlines()

openai.api_key = os.environ["OPENAI_API"]
app = Flask(__name__, template_folder='templates')
session = requests.Session()
dg = Deepgram(os.environ["DG_KEY"])

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': 'text/x-component',
    'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3',
    'Referer': 'https://instagram-videos.vercel.app/',
    'Next-Action': '2627efa1b8fdc3a3fc06d1fa89c5e9072ee9e54c',
    'Next-Router-State-Tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
    'Next-Url': '/',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Origin': 'https://instagram-videos.vercel.app',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}
ReelDownload = requests.Session()
ReelDownload.headers.update(headers)

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

def logprobs_to_probs(logprobs):
    probs = []
    for x in logprobs:
        probs.append(math.exp(x))
    return probs

def build(desc, transcription):
    return deEmojify(f"{desc} | {transcription}  ->")

def isEducational(desc, transcription):
    response = openai.Completion.create(
          model="ft:babbage-002:personal::8Tvt6kYy",
          prompt=build(
            desc=desc,
            transcription=transcription
          ),
          temperature=1,
          top_p=1,
          logprobs=25, # see probabilities of all of em
          frequency_penalty=0,
          presence_penalty=0,
          stop=["."]
        )
    print(response, desc, transcription)
    is_true = "true" in response["choices"][0]["text"].lower()
    return is_true

def reel_data(id):
    if not id:
        return {}
    data = session.get(f"https://www.instagram.com/api/v1/oembed/?hidecaption=0&maxwidth=540&url=https://www.instagram.com/reel/{id}").json()
    return data


def transcribe_large(audio_file):
    print("transcribing with lage file")
    source = {"buffer": audio_file, "mimetype":'audio/mp3'}
    res = dg.transcription.sync_prerecorded(source, options = {
        "punctuate": True,
        "model": 'general',
        "tier": 'enhanced'
        }
    )
    return res['results']['channels'][0]['alternatives'][0]['transcript']

def transcribe(audio_dir):
    with open(audio_dir, "rb") as audio_file:
        if os.path.getsize(audio_dir) > 25000000:
            print("Large file detected, transcribing with deepgram", os.path.getsize(audio_dir))
            transcript = transcribe_large(audio_file)
        else:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)['text']

    return transcript or ''

def reel_to_transcript(id):
    data = [f"https://www.instagram.com/reel/{id}/"]

    response = ReelDownload.post('https://instagram-videos.vercel.app/', headers=headers, json=data)
    data = json.loads(
        response.text.splitlines()[1].split("1:")[1]
    )
    try:
        videoUrl = data["data"]["videoUrl"]
    except KeyError:
        print("No video found", id)
        return "", None

    base = "/tmp/{id}" if not developement else "tmp/{id}"
    with open(f"{base}.mp4", "wb") as f:
        data = ReelDownload.get(videoUrl).content
        
        if len(data) > 200:
            f.write(data)
        else:
            print("Download Error", data)
            return "", None
        print(f"Downloaded {id}.mp4", os.path.exists(f"{base}.mp4"))

    video = VideoFileClip(f"{base}.mp4")
    try:
        video.audio.write_audiofile(f"{base}.mp3")
        video.close()
        transcript = transcribe(f"{base}.mp3")
        return transcript, base
    except Exception as er:
        if "write_audiofile" in str(er):
            print("NO Audio found")
            transcript = ""
            return "", base
        else:
            print("ERROR:", er)
            return "", base
# static files
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.route('/')
def scroll():
    return render_template('index.html')

@app.route("/edu")
def edu():
    return render_template("check.html")

@app.route('/api/get_reel')
def get_reel():
    return random.sample(videos, 10)


@app.route('/api/get_embed')
def get_embed():
    # Get ID from parameters
    id = request.args.get('id')
    data = reel_data(id)
    return data

@app.route("/api/predict", methods=["POST"])
def predict_route():
    data = request.get_json()
    vidId = data["videoId"]

    subtitles, base = reel_to_transcript(vidId)
    data = reel_data(vidId)
    description = data["title"]
    
    print("PREDICTING WITH")
    print("SUBTITLES:", subtitles)
    print("DESCRIPTION:", description)

    prediction = isEducational(subtitles, description)

    try:
        os.remove(base + ".mp3"), os.remove( base + ".mp4")
    except Exception as err:
        print(err)

    return {"response": prediction}


# main driver function
if __name__ == '__main__' and developement:
    app.run(port=80)