import os
import requests
import re
import json
import yaml

config_path = 'config.yml'


try:
    with open(config_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        bid_list = data.get('bid', [])
        reserve_source = data.get('reserve_source', False)
except FileNotFoundError:
    print("File not found")
    exit(-1)
except yaml.YAMLError as e:
    print(f"Parse error: {e}")
    exit(-1)


url_list = [f'https://www.bilibili.com/video/{bid}/' for bid in bid_list]
print(url_list)
cookie = os.environ.get('BiliCookie')
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def BiliBiliRequest(url):
    headers = {
        "Referer": url,
        "User-Agent": user_agent,
        "Cookie": cookie
    }   
    
    response = requests.get(url=url, headers=headers)
    html = response.text

    title = re.findall('title="(.*?)"', html)[0]
    print(f'Download 【{title}】 start...')

    info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
    json_data = json.loads(info)

    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']    

    video_content = requests.get(url=video_url, headers=headers).content
    print(f'Download 【{title}】 video succeed 🎉')

    audio_content = requests.get(url=audio_url, headers=headers).content
    print(f'Download 【{title}】 audio succeed 🎉')

    title = re.sub(r'[^\w\s]', '', title)
    os.makedirs(os.path.join('download_videos', title), exist_ok=True)
    video_path = os.path.join('download_videos', title, 'video-' + title + '.mp4')
    audio_path = os.path.join('download_videos', title, 'audio-' + title + '.mp4')
    
    with open(video_path, mode='wb') as v:
        v.write(video_content)

    with open(audio_path, mode='wb') as a:
        a.write(audio_content)
    
    return title, video_path, audio_path

def merge(filename, video_path, audio_path):
    saved_path = os.path.join('download_videos', filename, filename + '.mp4')
    cmd = fr"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac -strict experimental -map 0:v -map 1:a {saved_path} -loglevel quiet"
    os.system(cmd)
    if reserve_source == False:
        os.remove(video_path)
        os.remove(audio_path)
    print("Merge succeed 🎉")
    print("Download Fisished.")
    print("--"*10)


if __name__ == "__main__":
    os.makedirs('download_videos', exist_ok=True)
    for url in url_list:
        title, video_path, audio_path = BiliBiliRequest(url)
        merge(title, video_path, audio_path)