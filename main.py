import os
from cfg import VKCfg, DiscordCfg
from src.discord_bot.client import Music
from discord.ext import commands


def preparation():
    if os.path.isdir("media"):
        print("Media folder checked...")
    else:
        os.mkdir("media")
        print("Media folder created...")

    if os.path.isdir("media/music"):
        print("Music folder checked...")
    else:
        os.mkdir("media/music")
        print("Music folder created...")

    if os.path.isdir("media/music/keys"):
        print("Keys folder checked...")
    else:
        os.mkdir("media/music/keys")
        print("Keys folder created...")

    if os.path.isdir("media/music/mp3"):
        print("MP3 folder checked...")
    else:
        os.mkdir("media/music/mp3")
        print("MP3 folder created...")

    if os.path.isdir("media/music/segments"):
        print("Segments folder checked...")
    else:
        os.mkdir("media/music/segments")
        print("Segments folder created...")


def setup(bot_instance):
    bot_instance.add_cog(Music(bot=bot_instance, login=VKCfg.API_LOGIN, password=VKCfg.API_PASSWORD))


if __name__ == "__main__":
    preparation()

    print("-" * 40)
    print("Starting and configuring the bot...")

    os.environ["TOKEN"] = DiscordCfg.DISCORD_API_TOKEN

    bot = commands.Bot(command_prefix=commands.when_mentioned_or(DiscordCfg.COMMAND_PREFIX))


    @bot.event
    async def on_ready():
        print(f"{bot.user} has started successfully!")


    setup(bot_instance=bot)

    bot.run(os.getenv("TOKEN"))
