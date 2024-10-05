from pytube import YouTube as YT
from pytube import Playlist
from pytube.contrib.search import Search
import pytube
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
Songs_Path = os.getenv('SONGS_FOLDER')


async def norm(fn):
    cmd = f"ffmpeg -i {fn} -af \"volume=$(ffmpeg -i {fn} -af volumedetect -dn -sn -vn -f null /dev/null 2>&1 | grep mean | awk -F ' ' '{{x = $5; print (-30 - x)}}')dB\" -c:a libopus -b:a 320k {fn}.opus 2>/dev/null && mv {fn}.opus {fn}"
    #cmd = f"ffmpeg -i {fn} -af \"loudnorm=i=-5\" -c:a libopus -b:a 320k {fn}.opus && mv {fn}.opus {fn}"
    import asyncio
    proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return

def get_a_song(link):
    
    yt = YT(link, use_oauth=True, allow_oauth_cache=True)

    print("Title: ", yt.title)

    song_fn = "{Id}.{ext}".format(Id=yt.video_id, ext="webm")
    print(yt.watch_url)
    print(song_fn)
        
    if os.path.isfile("{dir}/{fn}".format(dir=Songs_Path, fn=song_fn)):
        print("File exist, skipping...")

    else:
        stream_datas = list(yt.streams.filter(only_audio=True))

        max_itag = ""
        max_kbps = -1
        max_type = ""
    
        for i in range(len(stream_datas)):
            parsed_html = BeautifulSoup(str(stream_datas[i]), "html.parser")
            kbps = 0

            try:
                kbps = int(parsed_html.find('stream:')["abr"][:-4])
            except:
                pass
            if kbps > max_kbps:
                max_kbps = kbps
                max_itag = parsed_html.find('stream:')["itag"]
                max_type = parsed_html.find('stream:')["mime_type"].split("/")[1]

        ys = yt.streams.get_by_itag(max_itag)
        ys.download(output_path = Songs_Path, filename = song_fn)

    return "{dir}/{fn}".format(dir=Songs_Path, fn=song_fn)

def parse_playlist(links):
    playlst = Playlist(links)
    return list(playlst.video_urls)

def parse_link(link):
    try:
        lst = parse_playlist(link)
        return lst
    except Exception as e:
        print(e)
        print("try single song")
        try:
            get_a_song(link)
            return link
        except Exception as e:
            print(e)
            print("Unknown link")
            return None

def search(query):
    search = Search(query)
    return search.results
    
if __name__ == '__main__':
    link = input("link: ")
    yt = YT(link, use_oauth=True, allow_oauth_cache=True)
    print("channel_id:", yt.channel_id)
    print("channel_url:", yt.channel_url)
    #print(parse_link(link))
    #for yt in search(link):
    #    print(yt.title)
