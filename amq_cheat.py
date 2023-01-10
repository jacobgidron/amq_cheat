import asyncio
import json
from time import sleep
import re

from selenium.common import ElementNotInteractableException
from shazamio import Shazam
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys, getopt, subprocess, shlex
import requests
import pandas as pd

# from xvfbwrapper import Xvfb

# def run():

print('Capture website stream')

# xvfb = Xvfb(width=1280, height=720, colordepth=24)

# xvfb.start()
# options = Options()
# options.add_argument("--headless")
driver = webdriver.Chrome()

url = 'https://animemusicquiz.com/'

driver.get(url)


# //*[@id="qpAnswerInput"]
# r"/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[3]/div[2]/input"
# context = driver.find_element('xpath',
#       r"/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[3]/div[2]/input").text
# context = driver.find_element('xpath',
#       r"/html/body/div[2]/div[1]/div[7]/div[2]/div[2]/div[1]/div/div[1]/textarea").text
# context = driver.find_element('xpath',"/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[3]/div[2]/input")
async def recognize():
    file_path = r" Z:\TEMP\sample.mp3"
    cmd = """./ffmpeg.exe -f dshow -i audio="VoiceMeeter Output (VB-Audio VoiceMeeter VAIO)" -y -t 00:00:04 Z:/TEMP/sample.mp3"""
    # cmd = """ ./ffmpeg.exe -f dshow -i audio="VoiceMeeter Output (VB-Audio VoiceMeeter VAIO)" -y -t 00:00:04 sample.mp3"""
    print(cmd)
    args = shlex.split(cmd)
    subprocess.Popen(args)
    sleep(6)
    shazam = Shazam()
    out = await shazam.recognize_song(r'Z:\TEMP\sample.mp3')
    if ('track' not in out.keys()) or 'title' not in out['track']:
        return False, None
    songe_title = out['track']['title']
    print(songe_title)
    return True, songe_title


loop = asyncio.get_event_loop()


# out = loop.run_until_complete(recognize())


# https://api.animethemes.moe/search?q={Bocchi%20The%20Rock}&page[limit]=1

#  answer is in
# /html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[2]
# number songs
# /html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[1]/div/span[1]

# start button
# /html/body/div[2]/div[1]/div[7]/div[1]/div[1]/div[1]/div[4]/h1
def find_anime(song):
    songe_title_clean = re.sub(r'\(.*\)', '', song).lower()
    print(songe_title_clean)
    tmp = requests.get(f"https://api.animethemes.moe/search?q={{{songe_title_clean}}}&page[limit]=1").json()
    if not tmp['search']['videos']:
        return None
    tmp_name = tmp['search']['videos'][0]['basename']
    print(tmp_name)
    camel_name = re.findall("[^-]+", tmp_name)[0]
    print(camel_name)
    lower_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel_name).lower()
    name_search = requests.get(f"https://api.animethemes.moe/search?q={{{lower_name}}}&page[limit]=1").json()
    if not tmp['search']['anime']:
        return None
    name = name_search['search']['anime'][0]['name']
    return name

def play_game():
    tmp = pd.read_json('mem.jsonl', lines=True)
    context = driver.find_element('xpath',
                                  "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[3]/div[2]/input")
    j = tmp.to_dict(orient='list')
    mem_dict = dict(zip(j['song'], j['anime']))

    ref_idx = driver.find_element('xpath',
                                  "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[1]/div/span[1]")
    true_ans = driver.find_element('xpath',
                                   "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[2]")
    count = driver.find_element('xpath',
                                "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[2]/div/div/div[1]/div[5]/div")
    while true_ans.is_displayed():
        status = False
        song = loop.run_until_complete(recognize())
        left = count.text
        while not status:
            status, song = loop.run_until_complete(recognize())

        if (song is not None):
            if (song in mem_dict.keys()):
                print(f"remembered that {song} is form  {mem_dict.get(song)} ")
                anime = mem_dict.get(song)
            else:
                anime = find_anime(song)
            try:
                context.send_keys(anime)
            except ElementNotInteractableException:
                print("ElementNotInteractableException giving up")
        else:
            print("song is None, giving up")

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
