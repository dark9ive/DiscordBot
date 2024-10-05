import discord
import yt
import asyncio
import os
from random import randint
from multiprocessing import Process, Manager
import dinner
import math
import time
import subprocess
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('MUSIC_KEY')
img_folder = os.getenv('IMG_FOLDER')

start_sign = "~"
ss_len = len(start_sign)

print(discord.__version__)
intents = discord.Intents.all()
client = discord.Client(intents=intents)


class MyQueue:
    def __init__(self):
        self.SongQueue = []
        self.TitleQueue = []
        return
    def push(self, link):
        Song = yt.YT(link, use_oauth=True, allow_oauth_cache=True)
        self.SongQueue.append(Song.watch_url)
        self.TitleQueue.append(Song.title)
        return
    def pushYT(self, Song):
        self.SongQueue.append(Song.watch_url)
        self.TitleQueue.append(Song.title)
        return
    def pushhead(self, link):
        if self.len() == 0:
            return self.push(link)
        Song = yt.YT(link, use_oauth=True, allow_oauth_cache=True)
        self.SongQueue.insert(1, Song.watch_url)
        self.TitleQueue.insert(1, Song.title)
        return
    def pop(self):
        returnval = (self.SongQueue[0], self.TitleQueue[0])
        self.SongQueue = self.SongQueue[1:]
        self.TitleQueue = self.TitleQueue[1:]
        return returnval
    def rm(self, idx):
        returnval = (self.SongQueue[idx], self.TitleQueue[idx])
        self.SongQueue = self.SongQueue[:idx] + self.SongQueue[idx+1:]
        self.TitleQueue = self.TitleQueue[:idx] + self.TitleQueue[idx+1:]
        return returnval
    def clear(self):
        self.SongQueue = []
        self.TitleQueue = []
        return
    def len(self):
        return len(self.SongQueue)

Queue = MyQueue()
dinner.load()

KeepPlay = 0
Playing = 0
loop = 0
vc = None
results = {}
Song_st = 0
queue_msg_url = None

CC_red = int(0xE74C3C)
CC_lightblue = int(0x53FAFA)
CC_lightgreen = int(0x33FF33)
CC_darkblue = int(0x3CA1CD)

def ClearQueue():
    global Queue
    Queue.clear()
    return

async def PlayMGR(msg):
    global vc
    global Queue
    global KeepPlay
    global Playing
    global loop
    global Song_st
    PlayProcess = None
    if not vc:
        msg.content = start_sign + "join"
        await on_message(msg)
    thread = None
    print(type(msg.channel))
    if type(msg.channel) == discord.threads.Thread:
        thread = msg.channel
    else:
        thread = await msg.create_thread(name=datetime.now().strftime("🎵 %Y/%m/%d %p %I:%M Music commands"))
    while Queue.len() > 0:
        filename = yt.get_a_song(Queue.SongQueue[0])
        print("Start playing {fn}".format(fn=filename))
        await yt.norm(filename)
        AS = await discord.FFmpegOpusAudio.from_probe(filename)

        embed_str = "[{title}]({link})".format(title=Queue.TitleQueue[0], link=Queue.SongQueue[0])
        embed = discord.Embed(title=":arrow_forward:  Now Playing",\
                description=embed_str, colour=discord.Colour(CC_darkblue))
        Song = yt.YT(Queue.SongQueue[0] ,use_oauth=True, allow_oauth_cache=True)
        embed.set_thumbnail(url=Song.thumbnail_url)
        embed.timestamp = datetime.now()
        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
        if loop == 1:
            await thread.send(embed=embed, delete_after=5)
        else:
            await thread.send(embed=embed)

        Playing = 1
        if not vc.is_connected():
            print("I'm not connected!")
            await vc.connect(timeout=10.0, reconnect=True)

        if filename == yt.Songs_Path + "/v86m2RdPSo8.webm":
            await thread.send(file = discord.File(f"{img_folder}/basilisk_time.gif"))
        if filename == yt.Songs_Path + "/dQw4w9WgXcQ.webm":
            await thread.send(file = discord.File(f"{img_folder}/rickroll.gif"))
        
        await asyncio.sleep(2)
        vc.play(AS)
        
        Song_st = time.time()

        while True:
            await asyncio.sleep(1)
            if KeepPlay == 0:
                print("User stops playing.")
                Playing = 0
            if vc.is_playing() == False:
                print("Finish playing a song.")
                Playing = 0
            if Playing == 0:
                break

        if vc:
            vc.stop()
        if KeepPlay == 0:
            ClearQueue()
        else:
            if loop == 0:
                Queue.pop()
            if loop == 2:
                link, title = Queue.pop()
                Queue.push(link)
        print(Queue.TitleQueue)

    embed_str = "The queue is empty."
    embed = discord.Embed(title=":wave: I'm leaving!",\
            description=embed_str)
    embed.timestamp = datetime.now()
    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
    await thread.send(embed=embed)
    await thread.delete()
    KeepPlay = 0
    
    if vc:
        vc.cleanup()
        await vc.disconnect()
        vc = None
    loop = 0
    return

async def play_a_song(vc, filename):
    return

async def not_in_same_channel(msg):
    embed_str = "Please join {channel} to use this command.".format(channel=vc.channel.name)
    embed = discord.Embed(title=":x:  You are not in the same voice channel with me!",\
            description=embed_str, colour=discord.Colour(CC_red))
    embed.timestamp = datetime.now()
    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
    await msg.reply(embed=embed)
    return


@client.event
async def on_ready():
    print('目前登入身份：', client.user, client.user.id)

@client.event
async def on_message(message):

    print(message.content)
    global Queue
    global KeepPlay
    global Playing
    global loop
    global vc
    global results
    global Song_st
    global queue_msg_url
    
    if message.author == client.user:
        return

    msg_id = str(message.author.id)+str(message.channel.id)
    vc = message.guild.voice_client

    if msg_id in results:
        idx = 0
        try:
            idx = int(message.content)
            if idx <= 0 or idx >= 11:
                raise IndexError("list index out of range")
        except:
            embed_str = "Canceling your search request..."
            embed = discord.Embed(title=":x:  Wrong index is given.",\
                    description=embed_str, colour=discord.Colour(CC_red))
            embed.timestamp = datetime.now()
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            await message.channel.send(embed=embed)
            del results[msg_id]
            return
        (res_arr, top_bool) = results[msg_id]
        if top_bool == True:
            message.content = start_sign + "pt {link}".format(link=res_arr[idx-1].watch_url)
        else:
            message.content = start_sign + "p {link}".format(link=res_arr[idx-1].watch_url)
        del results[msg_id]
        await on_message(message)
        return

    if message.content.startswith(start_sign) and not message.content.startswith("~~"):
        msg_arr = message.content.split(" ")
        msg_arr[0] = msg_arr[0].lower()

        if msg_arr[0][ss_len:] == "p" or msg_arr[0][ss_len:] == "play" or msg_arr[0][ss_len:] == "playtop" or msg_arr[0][ss_len:] == "pt":
            if len(msg_arr) <= 1:
                embed_str = ""
                if msg_arr[0][ss_len:] == "playtop" or msg_arr[0][ss_len:] == "pt":
                    embed_str = "Usage: {ss}playtop <Youtube URL>".format(ss=start_sign)
                else:
                    embed_str = "Usage: {ss}play/{ss}p <Youtube URL>".format(ss=start_sign)
                embed = discord.Embed(title=":x:  You must provide a youtube link!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.channel.send(embed=embed)
                return
            elif len(msg_arr) >= 3:
                embed_str = ""
                if msg_arr[0][ss_len:] == "playtop" or msg_arr[0][ss_len:] == "pt":
                    embed_str = "Usage: {ss}playtop <Youtube URL>".format(ss=start_sign)
                else:
                    embed_str = "Usage: {ss}play/{ss}p <Youtube URL>".format(ss=start_sign)
                embed = discord.Embed(title=":x:  Too many arguments!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.channel.send(embed=embed)
                return
            else:
                if message.author.voice == None:
                    embed_str = "Please join one first."
                    embed = discord.Embed(title=":x:  You are not in a voice channel!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.channel.send(embed=embed)
                    return
                if vc:
                    if message.author.voice.channel != vc.channel:
                        await not_in_same_channel(message)
                        return
                else:
                    message.content = "{ss}j".format(ss=start_sign)
                    await on_message(message)
                    if not vc.is_connected():
                        embed_str = "I Can't connect to your voice channel! Please try another one or call 張聖傑助教 to fix me!"
                        embed = discord.Embed(title=":x:  Error!",\
                                description=embed_str, colour=discord.Colour(CC_red))
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await message.reply(embed=embed)
                    
                embed_str = "Please wait..."
                embed = discord.Embed(title=":arrows_counterclockwise:  Processing your request.",\
                        description=embed_str, colour=discord.Colour(CC_lightblue))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                bot_msg = await message.reply(embed=embed)
                lst = yt.parse_link(msg_arr[1])
                if lst is None:
                    embed_str = "There's something wrong with your link!"
                    embed = discord.Embed(title="Error!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await bot_msg.edit(embed=embed)
                    if Queue.len() == 0:
                        embed_str = "Bye~"
                        embed = discord.Embed(title=":wave: Leaving.", description=embed_str)
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await message.channel.send(embed=embed)
                        await vc.disconnect()
                        vc = None
                    return
                elif type(lst) == str:
                    song = yt.YT(lst ,use_oauth=True, allow_oauth_cache=True)
                    if msg_arr[0][ss_len:] == "playtop" or msg_arr[0][ss_len:] == "pt":
                        Queue.pushhead(song.watch_url)
                    else:
                        Queue.push(song.watch_url)
                    embed_str = "Queued [{title}]({link}).".format(title=song.title, link=lst)
                    embed = discord.Embed(title=":white_check_mark:  Request accepted.",\
                            description=embed_str, colour=discord.Colour(CC_lightgreen))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await bot_msg.edit(embed=embed)
                else:
                    if msg_arr[0][ss_len:] == "playtop" or msg_arr[0][ss_len:] == "pt":
                        embed_str = "讓別人活命好嗎==".format(channel_name=vc.channel.name)
                        embed = discord.Embed(title=":x:  You can not playtop a playlist!",\
                                description=embed_str, colour=discord.Colour(CC_red))
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await bot_msg.edit(embed=embed)
                        if Queue.len() == 0:
                            embed_str = "Bye~"
                            embed = discord.Embed(title="Leaving.", description=embed_str)
                            embed.timestamp = datetime.now()
                            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                            await message.channel.send(embed=embed)
                            await vc.disconnect()
                            vc = None
                        return
                    

                    def worker(yt_lst, i, link):
                        song = yt.YT(link ,use_oauth=True, allow_oauth_cache=True)
                        title = song.title
                        yt_lst[i] = song
                        return

                    manager = Manager()
                    yt_lst = manager.list([None]*len(lst))
                    p = [None]*len(lst)
                    st = 0
                    for i in range(math.ceil(len(lst)/10)):
                        idx_list = []
                        for j in range(10):
                            idx = i*10+j
                            if idx >= len(lst):
                                break
                            p[idx] = (Process(target=worker, args=(yt_lst, idx, lst[idx])))
                            p[idx].start()
                            idx_list.append(idx)

                        for idx in idx_list:
                            p[idx].join()
                            if time.time() - st >= 2:
                                st = time.time()
                                embed_str = "Process: {i}/{total}\n".format(i=str(idx+1), total=len(lst))
                                for j in range(14):
                                    if abs(((idx+1)/len(lst)) - (j/13)) <= 1/26:
                                        embed_str += ":radio_button:"
                                    else:
                                        embed_str += "▬"
                                embed_str += "\n"
                                embed = discord.Embed(title=":arrows_counterclockwise:  Importing your playlist...",\
                                description=embed_str, colour=discord.Colour(CC_lightblue))
                                embed.timestamp = datetime.now()
                                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                                await bot_msg.edit(embed=embed)

                    for i in range(len(lst)):
                        Queue.pushYT(yt_lst[i])


                    playlst = yt.Playlist(msg_arr[1])
                    embed_str = "{num} song(s) queued from [{title}]({link})".format(num=str(len(lst)), title=playlst.title, link=msg_arr[1])
                    embed = discord.Embed(title=":white_check_mark:  Request accepted.",\
                            description=embed_str, colour=discord.Colour(CC_lightgreen))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await bot_msg.edit(embed=embed)
                if KeepPlay == 0:
                    KeepPlay = 1
                    await PlayMGR(message)

        elif msg_arr[0][ss_len:] == "s" or msg_arr[0][ss_len:] == "search" or msg_arr[0][ss_len:] == "st" or msg_arr[0][ss_len:] == "searchtop":
            if len(msg_arr) <= 1:
                embed_str = "Usage: {ss}search/{ss}s <query string>".format(ss=start_sign)
                embed = discord.Embed(title=":x:  You must provide a query string!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                return
            embed_str = "Please wait..."
            embed = discord.Embed(title=":arrows_counterclockwise:  Processing your request.",\
                    description=embed_str, colour=discord.Colour(CC_lightblue))
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            bot_msg = await message.reply(embed=embed)
            query_str = msg_arr[1]
            for i in range(2, len(msg_arr)):
                query_str += " " + msg_arr[i]
            result = yt.search(query_str)
            embed_str = ""
            for i in range(min(len(result), 10)):
                YT = result[i]
                embed_str += "**{i}.** [{title}]({url})\n".format(i=i+1, title=YT.title, url=YT.watch_url)
            embed = discord.Embed(title=":mag:  Search results for **\"{query}\"**\:".format(query=query_str), description=embed_str)
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            await bot_msg.edit(embed=embed)
            print(message.author.id)
            if msg_arr[0][ss_len:] == "s" or msg_arr[0][ss_len:] == "search":
                results[msg_id] = (result, False)
            elif msg_arr[0][ss_len:] == "st" or msg_arr[0][ss_len:] == "searchtop":
                results[msg_id] = (result, True)
            else:
                embed_str = "Command error! Please call 張聖傑助教 to fix me!".format(ss=start_sign)
                embed = discord.Embed(title=":x:  Error!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.channel.reply(embed=embed)
        
        elif msg_arr[0][ss_len:] == "q" or msg_arr[0][ss_len:] == "queue":

            bot_msg = await message.reply(embed=discord.Embed(description="thinking..."))
            queue_msg_url = bot_msg.jump_url
            sq_st = time.time()
            last_time = time.time()-1
            while True:
                if time.time() - last_time < 1:
                    await asyncio.sleep(0.2)
                    continue
                if queue_msg_url != bot_msg.jump_url:
                    embed = discord.Embed(title=":arrow_right:  There's a new queue message.",\
                            description=queue_msg_url)
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await bot_msg.edit(embed=embed)
                    break
                #else:
                embed = None
                if Queue.len() == 0:
                    embed = discord.Embed(title=":x:  The Queue is Empty!")
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    if bot_msg is None:
                        bot_msg = await message.reply(embed=embed)
                    else:
                        await bot_msg.edit(embed=embed)
                    break
                else:
                    last_time = time.time()
                    embed_str = ":arrow_forward: __Now Playing__\: :arrow_forward:\n"
                    embed_str += "[{title}]({link})\n\n".format(title=Queue.TitleQueue[0], link=Queue.SongQueue[0])

                    Song = yt.YT(Queue.SongQueue[0] ,use_oauth=True, allow_oauth_cache=True)
                    time_used = time.time() - Song_st
                    total_time = Song.length
                    bar_str = ""
                    for j in range(15):
                        if abs((time_used/total_time) - (j/14)) <= 1/28:
                            bar_str += ":radio_button:"
                        else:
                            bar_str += "▬"
                    total_time_str = ""
                    time_used_str = ""
                
                    time_used = int(time_used)
    
                    if total_time >= 3600:
                        total_time_str += "{:02d}:".format(total_time//3600)
                    total_time_str += "{:02d}:".format((total_time//60)%60)
                    total_time_str += "{:02d}".format(total_time%60)

                    if time_used >= 3600:
                        time_used_str += "{:02d}:".format(time_used//3600)
                    time_used_str += "{:02d}:".format((time_used//60)%60)
                    time_used_str += "{:02d}".format(time_used%60)
                    bar_str += "　`" + time_used_str + " / " + total_time_str + "`\n"

                    embed_str += bar_str
                    embed_str += "\n\n:arrow_down: __Up Next__\: :arrow_down:\n\n"
    
                    for i in range(1, min(Queue.len(), 11)):
                        embed_str += "**{idx}**. [{title}]({link})\n".format(idx=i, title=Queue.TitleQueue[i], link=Queue.SongQueue[i])
                    if Queue.len() - 11 > 0:
                        embed_str += "\n... and **{num}** more songs".format(num=Queue.len()-11)
                    embed = discord.Embed(title="Current Queue:", description=embed_str)

                    Song = yt.YT(Queue.SongQueue[0] ,use_oauth=True, allow_oauth_cache=True)
                    embed.set_thumbnail(url=Song.thumbnail_url)
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    if bot_msg is None:
                        bot_msg = await message.reply(embed=embed)
                    if time.time() - sq_st > 300:
                        bot_msg_new = await message.reply(embed=embed)
                        '''
                        embed = discord.Embed(title=":arrow_right:  There's a new queue message.",\
                                description=bot_msg_new.jump_url)
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await bot_msg.edit(embed=embed)
                        '''
                        await bot_msg.delete()
                        bot_msg = bot_msg_new
                        queue_msg_url = bot_msg.jump_url
                        sq_st = time.time()
                    else:
                        await bot_msg.edit(embed=embed)
            return
        elif msg_arr[0][ss_len:] == "join" or msg_arr[0][ss_len:] == "j":
            if vc:
                await message.reply("I'm already in a voice channel!")
                return
            if message.author.voice:
                channel = message.author.voice.channel
                try:
                    vc = await channel.connect(timeout=3.0, reconnect=False)
                except Exception as error:
                    print(error)
                    await message.reply("Failed to connect, please choose another voice channel.")
                    vc = None
                    return
            else:
                await message.reply("You are not in a voice channel, please join one first.")
        elif msg_arr[0][ss_len:] == "clear" or msg_arr[0][ss_len:] == "c":
            if Queue.len() <= 1:
                embed_str = "Nothing to clear!"
                embed = discord.Embed(title=":x:  Error!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
            else:
                link, title = Queue.pop()
                ClearQueue()
                Queue.push(link)
                embed_str = "Enjoy your last song and good night."
                embed = discord.Embed(title=":white_check_mark:  Queue cleared.",\
                        description=embed_str, colour=discord.Colour(CC_lightgreen))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                
        elif msg_arr[0][ss_len:] == "leave":
            if vc:
                if message.author.voice is None:
                    await not_in_same_channel(message)
                    return
                if message.author.voice.channel != vc.channel:
                    await not_in_same_channel(message)
                    return
                else:
                    if loop != 0:
                        loop = 0
                        message.content = "{ss}loop off".format(ss=start_sign)
                        await on_message(message)
                    if Queue.len() != 0:
                        KeepPlay = 0
                    else:
                        embed_str = "Bye~"
                        embed = discord.Embed(title=":wave: Leaving.", description=embed_str)
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await message.reply(embed=embed)
                        await vc.disconnect()
                        vc = None
            else:
                await message.reply("I'm not in a voice channel currenly!")

        elif msg_arr[0][ss_len:] == "skip":
            if Queue.len() == 0:
                await message.reply("There is no song playing now!")
                return
            if vc:
                if message.author.voice is None:
                    await not_in_same_channel(message)
                    return
                if message.author.voice.channel != vc.channel:
                    await not_in_same_channel(message)
                    return
                else:
                    if loop == 1:
                        message.content = "{ss}loop off".format(ss=start_sign)
                        await on_message(message)
                    Playing = 0
                    embed_str = "Please wait..."
                    embed = discord.Embed(title=":next_track:  Skipping current song.",\
                            description=embed_str, colour=discord.Colour(CC_darkblue))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed, delete_after=5)
            else:
                await message.reply("I'm not in a voice channel currenly!")
        elif msg_arr[0][ss_len:] == "shuffle":
            embed_str = "Please wait..."
            embed = discord.Embed(title="Shuffling...", description=embed_str)
            embed.timestamp = datetime.now()
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            bot_msg = await message.reply(embed=embed)
            for i in range(1, Queue.len()):
                j = randint(1, Queue.len()-1)
                if i == j:
                    continue
                tmp = Queue.SongQueue[i]
                Queue.SongQueue[i] = Queue.SongQueue[j]
                Queue.SongQueue[j] = tmp
                tmp = Queue.TitleQueue[i]
                Queue.TitleQueue[i] = Queue.TitleQueue[j]
                Queue.TitleQueue[j] = tmp
            embed = discord.Embed(title=":twisted_rightwards_arrows:  Shuffle complete.")
            embed.timestamp = datetime.now()
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            await bot_msg.edit(embed=embed)

        elif msg_arr[0][ss_len:] == "loop":
            if len(msg_arr) > 2 or len(msg_arr) == 1 or msg_arr[1] == "help" or msg_arr[1] == "h" or msg_arr[1] == "unknown":
                embed = discord.Embed()
                if len(msg_arr) > 2:
                    embed.title = ":x:  Too many arguments!"
                    embed.colour = discord.Colour(CC_red)
                elif len(msg_arr) == 1 or msg_arr[1] == "help" or msg_arr[1] == "h":
                    embed.title = ":repeat:  Loop help"
                    #embed.colour = discord.Colour(CC_lightblue)
                else:
                    embed.title = ":x:  Unknown arguments!"
                    embed.colour = discord.Colour(CC_red)

                embed.description = "Usage: {ss}loop [ one / o | queue / q | off / disable | status / stat / s | help / h ]".format(ss=start_sign)
                embed.add_field(name="{ss}loop one / {ss}loop o".format(ss=start_sign), value="Loop current track", inline=False)
                embed.add_field(name="{ss}loop queue / {ss}loop q".format(ss=start_sign), value="Loop the whole queue.", inline=False)
                embed.add_field(name="{ss}loop off / {ss}loop disable".format(ss=start_sign), value="Disable the loop.", inline=False)
                embed.add_field(name="{ss}loop status / {ss}loop stat / {ss}loop s".format(ss=start_sign), value="Show current loop status.", inline=False)
                embed.add_field(name="{ss}loop help / {ss}loop h".format(ss=start_sign), value="Show this help message.", inline=False)
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                return
            elif msg_arr[1] == "status" or  msg_arr[1] == "stat" or  msg_arr[1] == "s":
                if loop == 0:
                    embed_str = "Loop disabled."
                    embed = discord.Embed(title=":arrow_right:  Loop Disabled!",\
                            description=embed_str)
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                elif loop == 1:
                    embed_str = "Looping current song."
                    embed = discord.Embed(title=":repeat_one:  Loop Enabled!",\
                            description=embed_str, colour=discord.Colour(CC_lightblue))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                elif loop == 2:
                    embed_str = "Looping current list."
                    embed = discord.Embed(title=":repeat:  Loop Enabled!",\
                            description=embed_str, colour=discord.Colour(CC_lightblue))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                else:
                    embed_str = "Loop_Code = {loop}".format(loop=loop)
                    embed = discord.Embed(title=":x:  Loop error!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                return
            elif msg_arr[1] == "off" or msg_arr[1] == "disable" or msg_arr[1] == "one" or msg_arr[1] == "o" or msg_arr[1] == "queue" or msg_arr[1] == "q":
                if vc:
                    if message.author.voice is None:
                        await not_in_same_channel(message)
                        return
                    if message.author.voice.channel != vc.channel:
                        await not_in_same_channel(message)
                        return
                else:
                    embed_str = "Please invite me to a voice channel first."
                    embed = discord.Embed(title=":x:  I'm not in a voice channel currenly!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                if msg_arr[1] == "off" or msg_arr[1] == "disable":
                    loop = 0
                elif msg_arr[1] == "one" or msg_arr[1] == "o":
                    loop = 1
                elif msg_arr[1] == "queue" or msg_arr[1] == "q":
                    loop = 2
                message.content = "{ss}loop status".format(ss=start_sign)
                await on_message(message)
                return
            else:
                message.content = "{ss}loop unknown".format(ss=start_sign)
                await on_message(message)
                return

        elif msg_arr[0][ss_len:] == "rm" or msg_arr[0][ss_len:] == "remove":
            if len(msg_arr) <= 1:
                embed_str = "Usage: {ss}remove/{ss}rm <song index>".format(ss=start_sign)
                embed = discord.Embed(title=":x:  You must provide an song index!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                return
            elif len(msg_arr) >= 3:
                embed_str = "Usage: {ss}remove/{ss}rm <song index>".format(ss=start_sign)
                embed = discord.Embed(title=":x:  Too many arguments!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                return
            if vc:
                if message.author.voice is None:
                    await not_in_same_channel(message)
                    return
                if message.author.voice.channel != vc.channel:
                    await not_in_same_channel(message)
                    return
                idx = 0
                try:
                    idx = int(msg_arr[1])
                    if idx <= 0 or idx >= Queue.len():
                        raise IndexError("list index out of range")
                except:
                    embed_str = ""
                    if Queue.len() <= 1:
                        embed_str = "No song to delete!"
                    else:
                        embed_str = "Index out of range. ({si} ~ {ei})".format(si=1, ei=Queue.len()-1)
                    embed = discord.Embed(title=":x:  Wrong index is given.",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return

                else:
                    link, title = Queue.rm(idx)
                    embed_str = "Delete [{title}]({link})".format(title=title, link=link)
                    embed = discord.Embed(title=":wastebasket:  Song removed.",\
                            description=embed_str)
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
            else:
                embed_str = "Please invite me to a voice channel first."
                embed = discord.Embed(title=":x:  I'm not in a voice channel currenly!",\
                        description=embed_str, colour=discord.Colour(CC_red))

        elif msg_arr[0][ss_len:] == "dl":
            embed_str = ""
            if len(msg_arr) <= 1:
                embed_str = "Usage: {ss}dllink <Youtube URL>".format(ss=start_sign)
                embed = discord.Embed(title=":x:  You must provide a youtube link!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                return
            elif len(msg_arr) >= 3:
                embed_str = "Usage: {ss}dllink <Youtube URL>".format(ss=start_sign)
                embed = discord.Embed(title=":x:  Too many arguments!",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                return
            else:
                embed_str = "Please wait..."
                embed = discord.Embed(title=":arrows_counterclockwise:  Processing your request.",\
                        description=embed_str, colour=discord.Colour(CC_lightblue))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                bot_msg = await message.reply(embed=embed)
                try:
                    fn = yt.get_a_song(msg_arr[1]).split("/")[-1]
                    Song = yt.YT(msg_arr[1] ,use_oauth=True, allow_oauth_cache=True)
                    link = "https://darkknive.ebg.tw/songs/{fn}".format(fn=fn)
                    embed_str = "Download link for {name}:\n{link}".format(name=Song.title, link=link)
                    embed = discord.Embed(title=":white_check_mark:  Your Link is ready.",\
                            description=embed_str, colour=discord.Colour(CC_lightgreen))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await bot_msg.edit(embed=embed)
                except:
                    embed_str = "There's something wrong with your link!"
                    embed = discord.Embed(title="Error!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await bot_msg.edit(embed=embed)

            
        elif msg_arr[0][ss_len:] == "buffer" or msg_arr[0][ss_len:] == "buf":
            cmd = "du --max-depth=0 -h " + yt.Songs_Path
            size = os.popen(cmd).read().split("\t")[0]
            embed_str = "Local music buffer folder size is {size}".format(size=size)
            embed = discord.Embed(title="Local Buffer Size", description=embed_str)
            embed.timestamp = datetime.now()
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            await message.channel.send(embed=embed)

        elif msg_arr[0][ss_len:] == "meow":
            await message.channel.send("Nya~ UwU")

        elif msg_arr[0][ss_len:] == "ping":
            ping = 0.0
            if vc:
                ping = vc.average_latency*1000
            else:
                ping = client.latency*1000
            embed_str = "My last ping is {ping}ms.".format(ping=str(int(ping)))
            embed = discord.Embed(title=":ping_pong:  Pong!", description=embed_str)
            embed.timestamp = datetime.now()
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            await message.channel.send(embed=embed)

        elif msg_arr[0][ss_len:] == "random":
            embed_str = "Go fuck yourself."
            embed = discord.Embed(title="7414", description=embed_str)
            embed.timestamp = datetime.now()
            embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
            await message.channel.send(embed=embed)
        
        elif msg_arr[0][ss_len:] == "dinner":
            user = message.author.id
            if len(msg_arr) == 1:
                result = dinner.rand(user)
                if result is None:
                    embed_str = "Please use `{prefix}dinner add item_name random_prob` to set an item first.".format(prefix=start_sign)
                    embed = discord.Embed(title=":x:  You haven't set any items!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                else:
                    embed = discord.Embed(title=":fork_and_knife:  {name}, Eat {item} today!".format(name=message.author.display_name,\
                            item=result), colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                return
            elif msg_arr[1] == "add":
                if len(msg_arr) != 4:
                    embed_str = "Please use `{prefix}dinner add item_name random_prob` to set an item.".format(prefix=start_sign)
                    embed = discord.Embed(title=":x:  Wrong usage!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                else:
                    try:
                        msg_arr[3] = float(msg_arr[3])
                        if msg_arr[3] > 100.0 or msg_arr[3] < 0.0 or math.isnan(msg_arr[3]):
                            raise ValueError("not in range.")
                    except:
                        embed_str = "Your probability must be an float number between 0.0 ~ 100.0!"
                        embed = discord.Embed(title=":x:  Wrong usage!",\
                                description=embed_str, colour=discord.Colour(CC_red))
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await message.reply(embed=embed)
                        return
                    if not dinner.add(user, msg_arr[2], msg_arr[3]):
                        embed_str = "This restaurant has already been added to your list!"
                        embed = discord.Embed(title=":x:  Duplicate restaurant!",\
                                description=embed_str, colour=discord.Colour(CC_red))
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await message.reply(embed=embed)
                        return
                    else:
                        embed_str = "{item} has been added to your list with probability {prob}.".format(item=msg_arr[2], prob=msg_arr[3])
                        embed = discord.Embed(title=":white_check_mark:  Request accepted.",\
                                description=embed_str, colour=discord.Colour(CC_lightgreen))
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                        await message.reply(embed=embed)
                        return
            elif msg_arr[1] == "list":
                if len(msg_arr) != 2 and len(msg_arr) != 3:
                    embed_str = "Use `{prefix}dinner list (item_name)` to list all items (or specific item) and their probability.".format(\
                            prefix=start_sign)
                    embed = discord.Embed(title=":x:  Wrong usage!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                item = None
                if len(msg_arr) == 3:
                    item = msg_arr[2]
                res = dinner.query(user, item)
                if res is None:
                    embed_str = "Please use `{prefix}dinner add item_name random_prob` to set an item first.".format(prefix=start_sign)
                    embed = discord.Embed(title=":x:  You haven't set any items!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                item_idx = 1
                embed_str = ""
                for (item, weight) in res:
                    embed_str += "**{idx}.** {item}\nprob: {weight}\n".format(idx=item_idx, item=item, weight=weight)
                    item_idx += 1
                embed = discord.Embed(title=":fork_and_knife:  Your dinner list:",\
                        description=embed_str, colour=discord.Colour(CC_red))
                embed.timestamp = datetime.now()
                embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                await message.reply(embed=embed)
                return
            elif msg_arr[1] == "rm":
                if len(msg_arr) != 3:
                    embed_str = "Use `{prefix}dinner rm item_name`\nto remove specified item from your dinner list.".format(prefix=start_sign)
                    embed = discord.Embed(title=":x:  Wrong usage!",\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                if not dinner.rm(user, msg_arr[2]):
                    embed_str = "Use `{prefix}dinner add {item} random_prob` first.".format(prefix=start_sign, item=msg_arr[2])
                    embed = discord.Embed(title=":x:  You haven't add {item} to your dinner list!".format(item=msg_arr[2]),\
                            description=embed_str, colour=discord.Colour(CC_red))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
                else:
                    embed_str = "{item} has been removed from your list.".format(item=msg_arr[2])
                    embed = discord.Embed(title=":white_check_mark:  Request accepted.",\
                            description=embed_str, colour=discord.Colour(CC_lightgreen))
                    embed.timestamp = datetime.now()
                    embed.set_footer(text=client.user.display_name, icon_url=client.user.display_avatar)
                    await message.reply(embed=embed)
                    return
            else:
                await message.channel.send(embed=dinner.help())
                return
        else:
            await message.channel.send('Unknown command.')

client.run(KEY)
