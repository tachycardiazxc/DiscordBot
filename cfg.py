import datetime
import discord


# VK configuration


class VKCfg:
    API_LOGIN = ""
    API_PASSWORD = ""


# Discord configuration


class DiscordCfg:
    # API token
    DISCORD_API_TOKEN = ""

    # Message disappear timer
    DISCORD_MESSAGE_DISAPPEAR_TIMER = 30

    # Command prefix
    COMMAND_PREFIX = "?"


class NowPlayingEmbed:
    TITLE = None
    DESCRIPTION = None
    COLOR = None

    def __init__(self, song_artist, song_title, song_duration):
        self.TITLE = "Сейчас играет"
        self.DESCRIPTION = f"Исполнитель: {song_artist}\n" \
                           f"Название: {song_title}\n" \
                           f"Длительность: {datetime.timedelta(seconds=song_duration)}"
        self.COLOR = discord.Color.green()


class ConnectNotFoundEmbed:
    TITLE = ""
    DESCRIPTION = "Не могу найти канал для подключения." \
                  "Вызови `?join` находясь в канале."
    COLOR = discord.Color.green()


class ShuffleOkEmbed:
    TITLE = None
    DESCRIPTION = None
    COLOR = None

    def __init__(self, urls):
        self.TITLE = "Добавление в очередь и перемешивание."
        self.DESCRIPTION = f"Плейлист добавлен в очередь и случайно распределен!\n" \
                           f"Количество треков: {len(urls)}"
        self.COLOR = discord.Color.green()


class ShuffleErrorEmbed:
    TITLE = "Ошибочка..."
    DESCRIPTION = "Это не плейлист чувак!"
    COLOR = discord.Color.green()


class PlayPlaylistEmbed:
    TITLE = None
    DESCRIPTION = None
    COLOR = None

    def __init__(self, urls):
        self.TITLE = "Ошибочка..."
        self.DESCRIPTION = f"Плейлист добавлен в очередь!\n" \
                           f"Количество треков: {len(urls)}"
        self.COLOR = discord.Color.green()


class PlaySongEmbed:
    TITLE = None
    DESCRIPTION = None
    COLOR = None

    def __init__(self, url):
        self.TITLE = "Добавление в очередь."
        self.DESCRIPTION = f"Исполнитель: {url['artist']}\n" \
                           f"Название: {url['title']}\n" \
                           f"Длительность: {datetime.timedelta(seconds=url['duration'])}\n" \
                           f"Добавлено в очередь!"
        self.COLOR = discord.Color.green()


class PlayErrorEmbed:
    TITLE = None
    DESCRIPTION = None
    COLOR = None

    def __init__(self, search):
        self.TITLE = "Ошибка при попытке найти песню или плейлист=("
        self.DESCRIPTION = f"{search} эта штука не была найдена!(или я опять накосячил с кодом)"
        self.COLOR = discord.Color.green()


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
