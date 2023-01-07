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
async def recognize(context=None):
    cmd = """ ./ffmpeg.exe -f dshow -i audio="VoiceMeeter Output (VB-Audio VoiceMeeter VAIO)" -y -t 00:00:04 sample.mp3"""
    args = shlex.split(cmd)

    subprocess.Popen(args)
    sleep(6)
    shazam = Shazam()
    out = await shazam.recognize_song(r'C:\Users\Administrator\PycharmProjects\amq_cheat\sample.mp3')
    if ('track' not in out) or 'title' not in out['track']:
        return None, None, False
    songe_title = out['track']['title']
    songe_title_clean = re.sub(r'\(.*\)', '', songe_title).lower()
    print(songe_title)
    print(songe_title_clean)
    tmp = requests.get(f"https://api.animethemes.moe/search?q={{{songe_title_clean}}}&page[limit]=1").json()
    if not tmp['search']['videos']:
        return songe_title, None, True
    tmp_name = tmp['search']['videos'][0]['basename']
    print(tmp_name)
    camel_name = re.findall("[^-]+", tmp_name)[0]
    print(camel_name)
    lower_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel_name).lower()
    name_search = requests.get(f"https://api.animethemes.moe/search?q={{{lower_name}}}&page[limit]=1").json()
    if not tmp['search']['anime']:
        return songe_title, None, True
    name = name_search['search']['anime'][0]['name']
    print(f"entering res:{name}")
    if context is None:
        context = driver.find_element('xpath',
                                      "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[3]/div[2]/input")
    context.send_keys(f"{name}\n")

    # https://api.animethemes.moe/search?q={Bocchi%20The%20Rock}&page[limit]=1

    return songe_title, name, True


loop = asyncio.get_event_loop()


# out = loop.run_until_complete(recognize())


# https://api.animethemes.moe/search?q={Bocchi%20The%20Rock}&page[limit]=1

#  answer is in
# /html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[2]
# number songs
# /html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[1]/div/span[1]

# start button
# /html/body/div[2]/div[1]/div[7]/div[1]/div[1]/div[1]/div[4]/h1

def play_game():
    tmp = pd.read_json('mem.jsonl', lines=True)

    context = driver.find_element('xpath',
                                  "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[3]/div[2]/input")
    j = tmp.to_dict(orient='list')
    mem_dict = dict(zip(j['song'], j['anime']))

    song_idx = 0
    ref_idx = driver.find_element('xpath',
                                  "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[1]/div/span[1]")
    true_ans = driver.find_element('xpath',
                                   "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[1]/div[2]")
    count = driver.find_element('xpath',
                                "/html/body/div[2]/div[1]/div[7]/div[1]/div[2]/div[8]/div[2]/div[2]/div/div/div[1]/div[5]/div")
    while true_ans.is_displayed():
        # in_loop = asyncio.get_event_loop()
        # song, anime, status = await recognize()
        song, anime, status = loop.run_until_complete(recognize(context))
        # song, anime, status = in_loop.run_until_complete(recognize())
        # we failed

        # wait for song revel and save answer
        left = count.text
        while left != '':
            if not status:
                try:
                    song, anime, status = loop.run_until_complete(recognize())
                    if not status and song in mem_dict.keys():
                        context.send_keys(mem_dict.get(song))
                except ElementNotInteractableException:
                    print("ElementNotInteractableException giving up")
                    status = True
            print(f"{left} seconds left")
            sleep(2)
            left = count.text
        last_ans = true_ans.text
        if song not in mem_dict.keys():
            print(f"savimg {song}  with \b {last_ans}")
            mem_dict[song] = last_ans
            with open("mem.jsonl", "a") as mem_file:
                mem_file.write(json.dumps({"song": song,
                                           "anime": last_ans}))
                mem_file.write("\n")
            song_idx = ref_idx.text
        # wait to next round
        print("wating for next round")
        while song_idx == ref_idx.text:
            print(".", end="")
            sleep(2)
