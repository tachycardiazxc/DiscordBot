<h1 align="center">Music Discord Bot</h1>

---

<h3 align="center">Requirements</h3>

* Python 3.8
* FFMPEG

---

<h3 align="center">Installation</h3>

1) Open CMD
2) Create a directory
3) Clone project here
4) Open cfg.py in project folder and configure it with your settings
5) In CMD:

```shell
cd DiscordBot
pip install virtualenv
virtualenv -p=3.8 venv
.\venv\scripts\activate
pip install -r requirements.txt
python main.py
```

5) Wait until the program starts
6) Use it!

---

<h3 align="center">Features</h3>

* `?play` command working with VK albums or search
* if `?play` command used as a search it will provide you 5 variants if songs that you are able to choose
* Common commands such as `?skip`, `?leave`, `?pause` and others
* `?shuffle` command that shuffles a given album

---

<h3 align="center">Known issues</h3>

* The regular expression that works with album url cannot recognize all possible albums url
* After `?leave` command the bot leaves, but still tries to play next queued song, what leads to forever stored .wav file of next song, so if you use that bot and care about your storage space I recommend you to restart the bot sometimes, until I fix it(or you can help me with that), after restart and first `?play` use the mp3 folder removes all garbage
* Some unnecessary issues such as shitty code(try except blocks that catching `Exception` instead of real possible exceptions) 

---

<h3 align="center">Feature goals</h3>

* Add commands that allow to play random albums by genre like `?phonk`, `?hyprepop` and others

You can also request a feature, and I'll try to make it or you help me with it.