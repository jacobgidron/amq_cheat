import asyncio
import json
from time import sleep
import re

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.common import ElementNotInteractableException
from shazamio import Shazam
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys, getopt, subprocess, shlex
import requests
import pandas as pd

FILE_PATH = r"Z:\TEMP\sample.mp3"
SONG_TO_ANIME_SEARCH_PATTERN = "https://api.animethemes.moe/search?fields[search]=videos&q={{{}}}&page[limit]=1"
ANIME_SEARCH_PATTERN = "https://api.animethemes.moe/search?fields[search]=anime&q={{{}}}&page[limit]=1"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
shazam = Shazam()
url = 'https://animemusicquiz.com/'
driver.get(url)
async def recognize():
    cmd = """./ffmpeg.exe -loglevel quiet -stats -f dshow -i audio="VoiceMeeter Output (VB-Audio VoiceMeeter VAIO)" -y -t 00:00:04 Z:/TEMP/sample.mp3"""
    args = shlex.split(cmd)
    subprocess.call(args)
    out = await shazam.recognize(FILE_PATH)
    if ('track' not in out.keys()) or 'title' not in out['track']:
        return False, None
    songe_title = out['track']['title']
    print(songe_title)
    return True, songe_title


loop = asyncio.get_event_loop()

def find_anime(song):
    songe_title_clean = re.sub(r'\(.*\)', '', song).lower()
    print(songe_title_clean)
    res = requests.get(SONG_TO_ANIME_SEARCH_PATTERN.format(songe_title_clean)).json()
    if  (res is None) or "videos" not in res['search'] or  not res['search']['videos']:
        print("did not find the song's anime")
        return None
    video_filename = res['search']['videos'][0]['basename']
    print(video_filename)
    anime_name = re.findall("[^-]+", video_filename)[0]
    print(anime_name)
    lower_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', anime_name).lower()
    # if the name is __OP/ED the video filename then the first part is the anime name
    if "OP" in video_filename or "ED" in video_filename:
        return lower_name
    # else we try to get the name by searching the name we just got
    name_search = requests.get(ANIME_SEARCH_PATTERN.format(lower_name)).json()
    if not name_search['search']['anime']:
        return lower_name
    name = name_search['search']['anime'][0]['name']
    return name

def play_game():
    tmp = pd.read_json('mem.jsonl', lines=True)
    context = driver.find_element('id', "qpAnswerInput")

                                  
    j = tmp.to_dict(orient='list')
    mem_dict = dict(zip(j['song'], j['anime']))

    ref_idx = driver.find_element('id', "qpCurrentSongCount")
    true_ans = driver.find_element('id', "qpAnimeName")
    count = driver.find_element('id', "qpHiderText")
    while true_ans.is_displayed():
        status = False
        left = count.text
        while not status:
            status, song = loop.run_until_complete(recognize())

        if song is not None:
            if song in mem_dict.keys():
                print(f"remembered that {song} is form  {mem_dict.get(song)} ")
                anime = mem_dict.get(song)
            else:
                try:
                    anime = find_anime(song)
                except Exception as e:
                    print(e)
                    print(e.__traceback__)
            try:
                context.send_keys(anime)
            except Exception:
                print(f"anime is {anime}")
        else:
            print("did not find song, giving up")

        # wait for song revel and save answer
        while left != '':
            print(f"{left} seconds left")
            sleep(2)
            left = count.text

        if (song is not None) and (song not in mem_dict.keys()):
            ans = true_ans.text
            print(f"savimg {song}  with \b {ans}")
            mem_dict[song] = ans
            with open("mem.jsonl", "a") as mem_file:
                mem_file.write(json.dumps({"song": song,
                                           "anime": ans}))
                mem_file.write("\n")
        # wait to next round
        print("waiting for next round")
        song_idx = ref_idx.text
        print(f"{song_idx} == {ref_idx.text}")
        while song_idx == ref_idx.text:
            print(".", end="")
            sleep(2)
