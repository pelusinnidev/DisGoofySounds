# Instalación de dependencias necesarias para el bot y manejo de audio
!pip install discord.py[voice] PyNaCl youtube-dl
!apt install ffmpeg

import discord
from discord.ext import commands
import youtube_dl
import asyncio
import threading

# Configuración de los intents necesarios para el bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuración de youtube_dl para la descarga y conversión de audios
ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# "Base de datos" de audios con las URLs proporcionadas
audios = {
    "Ambatukum": "Sounds/ambatukum.mp3",
    "audio2": "https://youtu.be/-wllulJyJa8?si=doARzDsclS2ao7YJ",
    "audio3": "https://youtu.be/oxZxe092eqo?feature=shared",
    "audio4": "https://youtu.be/2J_LnGdDl5g?si=vIXGlmFSC9DHa2Om",
    "audio5": "https://youtu.be/G7eBQZj-EC8?si=SMZCRKYpCxsvc8Pg",
}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        return

    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        content = message.content.split()
        if len(content) == 1:
            await message.channel.send("Aquí tienes una lista de audios disponibles: " + ", ".join(audios.keys()))
        elif len(content) > 1 and content[1] in audios:
            audio_name = content[1]
            if message.author.voice:
                channel = message.author.voice.channel
                if message.guild.voice_client is None:
                    await channel.connect()
                voice_client = message.guild.voice_client
                async with message.channel.typing():
                    with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                        info = ydl.extract_info(audios[audio_name], download=False)
                        URL = info['formats'][0]['url']
                    voice_client.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options))
                    await message.channel.send(f"Reproduciendo {audio_name}...")
            else:
                await message.channel.send("Debes estar en un canal de voz para reproducir un audio.")
        else:
            await message.channel.send("No reconozco ese audio. Por favor, elige uno de la lista.")

    await bot.process_commands(message)

@bot.command()
async def join(ctx):
    """Se une al canal de voz del usuario."""
    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect()

@bot.command()
async def leave(ctx):
    """Sale del canal de voz."""
    await ctx.voice_client.disconnect()

# Función para ejecutar el bot en un hilo separado
def run_bot():
    bot.run('MTIwNDUxMDc1NjcwODY4MzgyNg.GSYevh.VlJM8-t40ByMGcKidpSGuVXEK5liD0VU9LHdcc')

# Crear y arrancar el hilo
bot_thread = threading.Thread(target=run_bot)
bot_thread.start()