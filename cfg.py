import datetime
import discord

# VK configuration


class VKCfg:

    API_LOGIN = ""
    API_PASSWORD = ""

# Discord configuration


class DiscordCfg:

    _false = False

    # API token
    DISCORD_API_TOKEN = ""

    # Message disappear timer
    DISCORD_MESSAGE_DISAPPEAR_TIMER = 30

    # Command prefix
    COMMAND_PREFIX = "?"

    if _false:
        class NowPlayingEmbed:

            _song_artist = str()
            _song_title = str()
            _song_duration = float()

            def __init__(self, song_artist, song_title, song_duration):

                self._song_artist = song_artist
                self._song_title = song_title
                self._song_duration = song_duration

            TITLE = "Сейчас играет"
            DESCRIPTION = f"Исполнитель: {_song_artist}\n" \
                          f"Название: {_song_title}\n" \
                          f"Длительность: {datetime.timedelta(seconds=_song_duration)}"
            COLOR = discord.Color.green()

        class ConnectNotFoundEmbed:

            TITLE = ""
            DESCRIPTION = "Не могу найти канал для подключения." \
                          "Вызови `?join` находясь в канале."
            COLOR = discord.Color.green()

        class ShuffleOkEmbed:

            _urls = list()

            def __init__(self, urls):

                self._urls = urls

            TITLE = "Добавление в очередь и перемешивание."
            DESCRIPTION = f"Плейлист добавлен в очередь и случайно распределен!\n" \
                          f"Количество треков: {len(_urls)}"
            COLOR = discord.Color.green()

        class ShuffleErrorEmbed:

            TITLE = "Ошибочка..."
            DESCRIPTION = "Это не плейлист чувак!"
            COLOR = discord.Color.green()

        class PlayPlaylistEmbed:

            _urls = list()

            def __init__(self, urls):

                self._urls = urls

            TITLE = "Ошибочка..."
            DESCRIPTION = f"Плейлист добавлен в очередь!\n" \
                          f"Количество треков: {len(_urls)}"
            COLOR = discord.Color.green()

        class PlaySongEmbed:

            _url = dict()

            def __init__(self, url):

                self._url = url

            TITLE = "Добавление в очередь."
            DESCRIPTION = f"Исполнитель: {_url['artist']}\n" \
                          f"Название: {_url['title']}\n" \
                          f"Длительность: {datetime.timedelta(seconds=_url['duration'])}\n" \
                          f"Добавлено в очередь!"
            COLOR = discord.Color.green()

        class PlayErrorEmbed:

            _search = str()

            def __init__(self, search):

                self._search = search

            TITLE = "Ошибка при попытке найти песню или плейлист=("
            DESCRIPTION = f"{_search} эта штука не была найдена!(или я опять накосячил с кодом)"
            COLOR = discord.Color.green()

        class PauseErrorEmbed:

            TITLE = ""
            DESCRIPTION = "Я сейчас ничего не играю..."
            COLOR = discord.Color.green()

        class PauseCtxMessage:

            MESSAGE = "Останавливаю ⏸️"

        class ResumeErrorEmbed:

            TITLE = ""
            DESCRIPTION = "Я не нахожусь в канале..."
            COLOR = discord.Color.green()

        class ResumeCtxMessage:

            MESSAGE = "Возобновляю ⏯️"

        class SkipErrorEmbed:

            TITLE = ""
            DESCRIPTION = "Я не нахожусь в канале..."
            COLOR = discord.Color.green()

        class LeaveErrorEmbed:

            TITLE = ""
            DESCRIPTION = "Я не нахожусь в канале..."
            COLOR = discord.Color.green()
