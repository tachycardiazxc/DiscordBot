from src.music_downloader.downloader import Downloader
import re
import os
import discord
from discord.ext import commands
import random
import asyncio
import sys
import traceback
from async_timeout import timeout
import datetime


class AlbumDownloader:

    def __init__(self, vk_audio):
        self._vk_audio = vk_audio

    @staticmethod
    async def _re_url(url: str):
        re_found = re.findall(r'[0-9]+', url)
        user_id = re_found[1]
        album_id = re_found[2]
        return user_id, album_id

    async def get_songs(self, url: str):
        owner_id, album_id = await self._re_url(url=url)
        result = self._vk_audio.get(owner_id=owner_id, album_id=album_id)
        return result


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog',
                 'queue', 'next', 'current', 'np', 'volume',
                 '_downloader', '_album_downloader',
                 'ctx')

    def __init__(self, ctx, downloader, album_downloader):
        self.ctx = ctx

        self._downloader = downloader
        self._album_downloader = album_downloader

        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            self.current = source
            song_cover_link, song_name, song_duration, segments_prefix, song_file_name, song_title, song_artist = await self._downloader.download(
                song=source, user_id=str(self.ctx.author.id))
            source = discord.FFmpegPCMAudio(f"media/music/mp3/{song_file_name}_{segments_prefix}.wav", )
            try:
                self._guild.voice_client.play(
                    source,
                    after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set)
                )
                embed = discord.Embed(title="Сейчас играет",
                                      description=f"Исполнитель: {song_artist}\n"
                                                  f"Название: {song_title}\n"
                                                  f"Длительность: {datetime.timedelta(seconds=song_duration)}",
                                      color=discord.Color.green())
                if song_cover_link is not None:
                    embed.set_image(url=song_cover_link)
                self.np = await self._channel.send(embed=embed)
            except AttributeError:
                pass
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None
            try:
                os.remove(f"media/music/mp3/{song_file_name}_{segments_prefix}.wav")
            except OSError:
                pass
            await self.np.delete()

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot, login, password):
        self.bot = bot
        self.players = {}
        self._md = Downloader(login=login, password=password)
        self._ad = AlbumDownloader(vk_audio=self._md.vk_audio)

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx, downloader=self._md, album_downloader=self._ad)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='join', aliases=['connect', 'j'], description="connects to voice")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = discord.Embed(title="",
                                      description="Не могу найти канал для подключения."
                                                  "Вызови `?join` находясь в канале.",
                                      color=discord.Color.green())
                await ctx.send(embed=embed)
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

    @commands.command(name='shuffle', aliases=['s', 'Shuffle'], description="Plays music and shuffle it")
    async def shuffle_(self, ctx, *, search: str):
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        if "http" in search:
            urls = await self._ad.get_songs(url=search)
            embed = discord.Embed(title="Добавление в очередь и перемешивание.",
                                  description=f"Плейлист добавлен в очередь и случайно распределен!",
                                  color=discord.Color.green())
            np = await ctx.channel.send(embed=embed)
            await asyncio.sleep(10)
            await np.delete()
            random.shuffle(urls)
            for url in urls:
                await player.queue.put(url)
        else:
            await ctx.send("Это не плейлист чувак!")

        await self._garbage_collector()
        await ctx.message.delete()

    @staticmethod
    async def _garbage_collector():
        mp3_files = os.listdir("media/music/mp3/")
        for file in mp3_files:
            try:
                os.remove(f"media/music/mp3/{file}")
            except PermissionError:
                pass

    @commands.command(name='play', aliases=['sing', 'p'], description="streams music")
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses downloader.py to automatically search and retrieve a song or a playlist.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using downloader and VK API. This could be a simple search or playlist URL.
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        if "http" in search:
            urls = await self._ad.get_songs(url=search)
            embed = discord.Embed(title="Добавление в очередь.",
                                  description=f"Плейлист добавлен в очередь!",
                                  color=discord.Color.green())
            np = await ctx.channel.send(embed=embed)
            await asyncio.sleep(10)
            await np.delete()
            for url in urls:
                await player.queue.put(url)
        else:
            url = await self._md.get_song(search=search)
            if url is not None:
                await player.queue.put(await self._md.get_song(search=search))
                embed = discord.Embed(title="Добавление в очередь.",
                                      description=f"{search} добавлена в очередь!",
                                      color=discord.Color.green())
                try:
                    embed.set_image(url=url['track_covers'][1])
                except Exception:
                    pass
                np = await ctx.channel.send(embed=embed)
                await asyncio.sleep(10)
                await np.delete()
            else:
                embed = discord.Embed(title="Ошибка при попытке найти песню или плейлист=(",
                                      description=f"{search} эта штука не была найдена!(или я опять накосячил с кодом)",
                                      color=discord.Color.green())
                np = await ctx.channel.send(embed=embed)
                await asyncio.sleep(10)
                await np.delete()
        await self._garbage_collector()
        await ctx.message.delete()

    @commands.command(name='pause', description="pauses music")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(title="", description="I am currently not playing anything",
                                  color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif vc.is_paused():
            return

        vc.pause()
        msg = await ctx.send("Останавливаю ⏸️")
        await ctx.message.delete()
        await asyncio.sleep(10)
        await msg.delete()

    @commands.command(name='resume', description="resumes music")
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        msg = await ctx.send("Возобновляю ⏯️")
        await ctx.message.delete()
        await asyncio.sleep(10)
        await msg.delete()

    @commands.command(name='skip', description="skips to next song in queue")
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.send(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.message.delete()

    @commands.command(name='leave', aliases=["stop", "dc", "disconnect", "bye"],
                      description="stops music and disconnects from voice")
    async def leave_(self, ctx):
        """Stop the currently playing song and destroy the player.
        This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.send(embed=embed)

        await ctx.message.delete()
        await self.cleanup(ctx.guild)

        mp3_files = os.listdir("media/music/mp3")
        for file in mp3_files:
            try:
                if ctx.author.id in file:
                    os.remove(f"media/music/mp3/{file}")
            except Exception:
                continue
