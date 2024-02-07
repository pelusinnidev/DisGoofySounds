import discord
from discord.ext import commands
import youtube_dl

# Configuración de los intents necesarios para el bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuración de youtube_dl para la descarga y conversión de audios
ytdl_format_options = {
    'format':
    'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl':
    '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames':
    True,
    'noplaylist':
    True,
    'nocheckcertificate':
    True,
    'ignoreerrors':
    False,
    'logtostderr':
    False,
    'quiet':
    True,
    'no_warnings':
    True,
    'default_search':
    'auto',
    'source_address':
    '0.0.0.0',
}

ffmpeg_options = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# "Base de datos" de audios con las URLs proporcionadas
audios = {
    "Ambatukam": "Sounds/ambatukam.mp3",
    # Añade más audios aquí, asegurándote de que las rutas sean correctas
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
      await message.channel.send(
          "Aquí tienes una lista de audios disponibles: " +
          ", ".join(audios.keys()))
    elif len(content) > 1 and content[1] in audios:
      audio_name = content[1]
      if message.author.voice:
        channel = message.author.voice.channel
        if message.guild.voice_client is None:
          await channel.connect()
        voice_client = message.guild.voice_client
        async with message.channel.typing():
          if audio_name in audios and audios[audio_name].startswith("http"):
            # Reproducir desde URL
            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
              info = ydl.extract_info(audios[audio_name], download=False)
              URL = info['formats'][0]['url']
            voice_client.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options))
          else:
            # Reproducir archivo local
            voice_client.play(
                discord.FFmpegPCMAudio(audios[audio_name], **ffmpeg_options))
          await message.channel.send(f"Reproduciendo {audio_name}...")
      else:
        await message.channel.send(
            "Debes estar en un canal de voz para reproducir un audio.")
    else:
      await message.channel.send(
          "No reconozco ese audio. Por favor, elige uno de la lista.")

  await bot.process_commands(message)


@bot.command()
async def join(ctx):
  """Se une al canal de voz del usuario."""
  if ctx.author.voice:
    channel = ctx.author.voice.channel
    await channel.connect()
  else:
    await ctx.send("Debes estar en un canal de voz para usar este comando.")


@bot.command()
async def leave(ctx):
  """Sale del canal de voz."""
  voice_client = ctx.message.guild.voice_client
  if voice_client.is_connected():
    await voice_client.disconnect()
  else:
    await ctx.send("El bot no está en un canal de voz.")


bot.run('MTIwNDUxMDc1NjcwODY4MzgyNg.GbRoDg.SVohVri37dQvoMZDM_mt_VUw39XOXMPZFF5mtI')