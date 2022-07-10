from src.music_downloader.downloader import Downloader
from cfg import API_LOGIN, API_PASSWORD
import asyncio


if __name__ == "__main__":
    downloader = Downloader(login=API_LOGIN, password=API_PASSWORD)
    asyncio.run(downloader.download(search="Камбулат привет", user_id="38712375"))
