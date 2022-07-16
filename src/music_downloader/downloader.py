import os
import random
import time
import m3u8
import requests
import vk_api
from vk_api import VkApi
from vk_api.audio import VkAudio
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from natsort import natsorted
import re

vk_api.audio.RPS_DELAY_LOAD_SECTION = 0
vk_api.audio.RPS_DELAY_RELOAD_AUDIO = 0


class Downloader:

    def __init__(self, login: str, password: str):
        self._vk_session = VkApi(
            login=login,
            password=password,
            api_version='5.81'
        )
        self._vk_session.auth()

        self.vk_audio = VkAudio(self._vk_session)

    async def download(self, song, user_id: str):
        random_suffix = await self._generate_random_suffix(user_id=user_id)
        song_cover_link, song_url, song_name, song_duration, song_file_name, song_title, song_artist = \
            await self._get_song_info(raw_song=song)
        cleaned_segments = await self._clean_segments(segments=await self._get_song_segments(uri=song_url))
        downloaded_segments = await self._download_song_by_segments(cleaned_segments=cleaned_segments,
                                                                    m3u8_url=song_url, )
        await self._convert_ts_to_mp3(suffix=random_suffix, song_name=song_file_name, segments=downloaded_segments)
        return song_cover_link, song_name, song_duration, random_suffix, song_file_name, song_title, song_artist

    async def get_song(self, search):
        try:
            result = self.vk_audio.search(q=search, count=5)
        except StopIteration:
            return None
        return result

    @staticmethod
    async def _get_song_info(raw_song):
        try:
            song_cover_link = raw_song['track_covers'][1]
        except IndexError:
            song_cover_link = None
        song_url = raw_song['url']
        song_name = raw_song['title'] + " " + raw_song['artist']
        song_title = raw_song['title']
        song_artist = raw_song['artist']
        song_file_name_list = re.findall(r"\w+", song_name)
        song_file_name = ""
        for s in song_file_name_list:
            song_file_name += s + " "
        song_file_name.strip(" ")
        song_duration = raw_song['duration']
        return song_cover_link, song_url, song_name, song_duration, song_file_name, song_title, song_artist

    @staticmethod
    async def _get_song_segments(uri: str):
        return m3u8.load(uri=uri).data.get("segments")

    @staticmethod
    async def _clean_segments(segments: list):
        cleaned_segments = {}

        for segment in segments:
            segment_uri = segment.get("uri")

            extended_segment = {
                "segment_method": None,
                "method_uri": None
            }
            if segment.get("key").get("method") == "AES-128":
                extended_segment["segment_method"] = True
                extended_segment["method_uri"] = segment.get("key").get("uri")
            cleaned_segments[segment_uri] = extended_segment
        return cleaned_segments

    @staticmethod
    async def _download_song_by_segments(cleaned_segments: dict, m3u8_url: str):
        downloaded_segments = []
        for uri in cleaned_segments:
            audio = requests.get(url=m3u8_url.replace("index.m3u8", uri))

            downloaded_segments.append(audio.content)

            if cleaned_segments.get(uri).get("segment_method") is not None:
                key_uri = cleaned_segments.get(uri).get("method_uri")
                key = await Downloader._download_key(key_uri=key_uri)

                iv = downloaded_segments[-1][0:16]
                ciphered_data = downloaded_segments[-1][16:]

                cipher = AES.new(key, AES.MODE_CBC, iv=iv)
                data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
                downloaded_segments[-1] = data

        return b''.join(downloaded_segments)

    @staticmethod
    async def _download_key(key_uri: str):
        return requests.get(url=key_uri).content

    @staticmethod
    async def _generate_random_suffix(user_id: str):
        rand_len = random.randint(8, 16)
        suffix = f"{user_id}_"
        for i in range(rand_len):
            rand = random.randint(0, 1)
            if rand == 0:
                suffix += chr(random.randint(65, 90))
            else:
                suffix += chr(random.randint(97, 122))
        return suffix

    @staticmethod
    async def _convert_ts_to_mp3(suffix: str, song_name: str, segments: bytes):
        with open(f'media/music/segments/segment_{suffix}.ts', 'w+b') as f:
            f.write(segments)
        os.system(f'ffmpeg -i "media/music/segments/segment_{suffix}.ts" -vcodec copy '
                  f'-acodec copy -vbsf h264_mp4toannexb "media/music/mp3/{song_name}_{suffix}.wav"')
        try:
            os.remove(f'media/music/segments/segment_{suffix}.ts')
        except PermissionError:
            async with time.sleep(5):
                os.remove(f'media/music/segments/segment_{suffix}.ts')
