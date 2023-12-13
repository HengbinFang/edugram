
from moviepy.video.io.VideoFileClip import VideoFileClip
from deepgram import Deepgram
import threading
import requests
import openai
import json
import os

# USING THE VIDEOS WE GOT FROM THE INSTAGRAM API, WE TRANSCRIBE THEM

dg = Deepgram("")
openai.api_key = ""

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
ses = requests.Session()
ses.headers.update(headers)

def transcribe_large(audio_file):
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

    return transcript or ' '

def reel_to_transcript(id):
    data = [f"https://www.instagram.com/reel/{id}/"]

    response = ses.post('https://instagram-videos.vercel.app/', headers=headers, json=data)
    print(response.text)
    data = json.loads(
        response.text.splitlines()[1].split("1:")[1]
    )
    try:
        videoUrl = data["data"]["videoUrl"]
    except KeyError:
        print("No video found", id)
        return "", None

    base = f"files/{id}"
    with open(f"{base}.mp4", "wb") as f:
        data = ses.get(videoUrl).content
        
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
    
ids = {}
with open("vid_data.txt", "r") as file:
    data = file.read().splitlines()
with open("new_data.txt", "r", encoding="utf-8") as file:
    db = file.read().splitlines()

print(len(data))
for x in db:
    id, transcript = x.split("|||")
    for p in data:
        if id in p:
            data.remove(p)
            break
print(len(data))

def thread():
    while 1:
        print("new iteration")
        try:
            x = data.pop()
        except IndexError:
            break

        id, transcript = x.split("|||")
        if not transcript:
            transcript, base = reel_to_transcript(id)
            ids[id] = transcript
            try:
                if base:
                    os.remove(f"{base}.mp4")
                    os.remove(f"{base}.mp3")
            except Exception as er:
                print(er)
            ids[id] = transcript
        
        with open("new_data.txt", "a",  encoding="utf-8") as file:
            file.write(f"{id}|||{transcript}\n")

        
        print(f"{id}|||{transcript}")
print('starting threads')
threads = [threading.Thread(target=thread) for _ in range(5)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
print("Done!")