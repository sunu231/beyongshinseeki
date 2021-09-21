import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import time
import asyncio
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import os

bot = commands.Bot(command_prefix='!')
client = discord.Client()

user = []
musictitle = []
song_queue = []
musicnow = []

def title(msg):
     global music

     YDL_OPTIONS = {'format' : 'bestaudio', 'noplaylist':'True'}
     FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

     options = webdriver.ChromeOptions()
     options.add_argument("headless")

     driver = load_chrome_driver()
     driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
     source = driver.page_source
     bs = bs4.BeautifulSoup(source, 'lxml')
     entire = bs.find_all('a', {'id': 'video-title'})
     entireNum = entire[0]
     music = entireNum.text.strip()
    
     musictitle.append(music)
     musicnow.append(music)
     test1 = entireNum.get('href')
     url = 'https://www.youtube.com'+test1
     with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
     URL = info['formats'][0]['url']

     driver.quit()

     return music, URL

def play(ctx):
    global vc
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(app.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 

def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

    else:
        if not vc.is_playing():
            client.loop.create_task(vc.disconnect())

def load_chrome_driver():
      
    options = webdriver.ChromeOptions()

    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)


@bot.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(bot.user.name)
    print('connection was succesful')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("노래"))
    
    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')
         
@bot.command()
async def w(ctx, *, url):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try: 
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("아무도 없네요...")

    YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + url + "을(를) 노래하고 있습니다.", color = 0x00ff00))
    else:
        await ctx.send("이미 노래를 부르고 있습니다!")

@bot.command()
async def p(ctx, *, msg):

    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("아무도 없넹...")

    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
        driver = load_chrome_driver()
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl 

        driver.quit()

        musicnow.insert(0, entireText)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + musicnow[0] + "을(를) 재생하고 있습니다.", color = 0x00ff00))
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    else:
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send(embed = discord.Embed(title= "노래 예약", description = "다음곡은" + result + "을 부르겠습니다!", color = 0x00ff00))


@bot.command()
async def 대기열추가(ctx, *, msg):
    user.append(msg)
    result, URLTEST = title(msg)
    song_queue.append(URLTEST)
    await ctx.send(result + "를 재생목록에 추가했어요!")

@bot.command()
async def 대기열삭제(ctx, *, number):
    try:
        ex = len(musicnow) - len(user)
        del user[int(number) - 1]
        del musictitle[int(number) - 1]
        del song_queue[int(number)-1]
        del musicnow[int(number)-1+ex]
            
        await ctx.send("대기열이 정상적으로 삭제되었습니다.")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없어 삭제할 수 없어요!")
        else:
            if len(list) < int(number):
                await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
            else:
                await ctx.send("숫자를 입력해주세요!")

@bot.command()
async def 목록(ctx):
    if len(musictitle) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
            
        await ctx.send(embed = discord.Embed(title= "노래목록", description = Text.strip(), color = 0x00ff00))

@bot.command()
async def 목록재생(ctx):

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if len(user) == 0:
        await ctx.send("아직 아무노래도 등록하지 않았어요.")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("노래가 이미 재생되고 있어요!")

@bot.command()
async def s(ctx):
    if vc.is_playing():
        vc.stop()
        await ctx.send(embed = discord.Embed(title= "노래 취소", description = musicnow[0] + " 를 그만 부르겠습니다!", color = 0x00ff00))
    else:
        await ctx.send("지금 노래를 부르고 있지 않습니다!")

@bot.command()
async def q(ctx):
    try:
        await vc.disconnect()
    except:
        await ctx.send("이미 그 채널에 속해있지 않아요")

@bot.command()
async def n(ctx):   
    if not vc.is_playing():
        await ctx.send("지금은 노래를 부르지 않고있습니다!")
    else:
        await ctx.send(embed = discord.Embed(title = "지금노래", description = "현재 " + musicnow[0] + " 을(를) 부르고 있습니다!", color = 0x00ff00))

bot.run('ODg4NjA2OTcwNjExODkyMjg0.YUVJuw.goW_-WyxKCVT8vLcP4CbbTyuKPc')