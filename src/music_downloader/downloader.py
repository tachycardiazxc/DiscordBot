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


class Downloader:

    def __init__(self, login: str, password: str):
        self._vk_session = VkApi(
            login=login,
            password=password,
            api_version='5.81'
        )
        self._vk_session.auth()

        self._vk_audio = VkAudio(self._vk_session)

    async def download(self, search: str, user_id: str):
        song = await self._get_song(search=search)
        song_cover_link, song_url, song_name, song_duration = await self._get_song_info(raw_song=song)
        segments = await self._clean_segments_segments(segments=await self._get_song_segments(uri=song_url))
        segments_prefix = await self._download_song_by_segments(cleaned_segments=segments,
                                                                m3u8_url=song_url,
                                                                user_id=user_id)
        await self._compile_audio(prefix=segments_prefix)
        await self._convert_ts_to_mp3(prefix=segments_prefix, song_name=song_name)
        await self._download_cover(prefix=segments_prefix, song_name=song_name, cover_link=song_cover_link)
        return song_cover_link, song_name, song_duration

    async def _get_song(self, search):
        try:
            result = next(self._vk_audio.search_iter(q=search))
        except vk_api.VkAudioException:
            return None
        return result

    @staticmethod
    async def _get_song_info(raw_song):
        song_cover_link = raw_song['track_covers'][1]
        song_url = raw_song['url']
        song_name = raw_song['title'] + " " + raw_song['artist']
        song_duration = raw_song['duration']
        return song_cover_link, song_url, song_name, song_duration

    @staticmethod
    async def _get_song_segments(uri: str):
        return m3u8.load(uri=uri).data.get("segments")

    @staticmethod
    async def _clean_segments_segments(segments: list):
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
    async def _download_song_by_segments(cleaned_segments: dict, m3u8_url: str, user_id):
        uris = cleaned_segments.keys()
        random_prefix = await Downloader._generate_random_prefix(user_id=user_id)
        for uri in uris:
            segment_name = uri.split(".")
            audio = requests.get(url=m3u8_url.replace("index.m3u8", uri))
            open(f"media/music/segments/{segment_name[0]}_{random_prefix}.{segment_name[1]}", "wb").write(audio.content)
            if cleaned_segments.get(uri).get("segment_method") is not None:
                key_uri = cleaned_segments.get(uri).get("method_uri")
                await Downloader._download_key(key_uri=key_uri, prefix=random_prefix)

                f = open(f"media/music/segments/{segment_name[0]}_{random_prefix}.{segment_name[1]}", "rb")
                iv = f.read(16)
                ciphered_data = f.read()

                key = open(f"media/music/keys/key_{random_prefix}.pub", "rb").read()
                cipher = AES.new(
                    key,
                    AES.MODE_CBC,
                    iv=iv
                )
                data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
                open(f"media/music/segments/{segment_name[0]}_{random_prefix}.{segment_name[1]}", "wb").write(data)
                os.remove(f"media/music/keys/key_{random_prefix}.pub")
        return random_prefix

    @staticmethod
    async def _download_key(key_uri: str, prefix: str):
        key = requests.get(url=key_uri)
        open(f"media/music/keys/key_{prefix}.pub", "wb").write(key.content)

    @staticmethod
    async def _generate_random_prefix(user_id: str):
        rand_len = random.randint(8, 16)
        prefix = f"{user_id}_"
        for i in range(rand_len):
            rand = random.randint(0, 1)
            if rand == 0:
                prefix += chr(random.randint(65, 90))
            else:
                prefix += chr(random.randint(97, 122))
        return prefix

    @staticmethod
    async def _compile_audio(prefix: str):
        segments_path = "media/music/segments/"
        segments_file = os.listdir(segments_path)
        for file in segments_file:
            f = open(f"{segments_path}/{file}", "rb").read()
            open(f"media/music/mp3/{prefix}.ts", "ab").write(f)
            try:
                os.remove(f"{segments_path}/{file}")
            except PermissionError:
                async with time.sleep(5):
                    os.remove(f"{segments_path}/{file}")

    @staticmethod
    async def _convert_ts_to_mp3(prefix: str, song_name: str):
        os.system(f'ffmpeg -i "media/music/mp3/{prefix}.ts" "media/music/mp3/{song_name}_{prefix}.mp3"')
        try:
            os.remove(f"media/music/mp3/{prefix}.ts")
        except PermissionError:
            async with time.sleep(5):
                os.remove(f"media/music/mp3/{prefix}.ts")

    @staticmethod
    async def _download_cover(prefix: str, song_name: str, cover_link: str):
        response = requests.get(url=cover_link)
        open(f"media/img/{song_name}_{prefix}.jpg", "wb").write(response.content)
