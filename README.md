# server-mycroft

Public interface to get speak via webrequest
I use this android app with a speak widget 

[https://play.google.com/store/apps/details?id=schaefferdstudio.voicecontrolweb](https://play.google.com/store/apps/details?id=schaefferdstudio.voicecontrolweb)
# Changes:
Enter the codes which you allow to request mycroft
- `codes = ['xxxx', 'xxxx']`

Open terminal
- `alsamixer`

Search the Soundcard and the device which mycroft use by your raspberry
After that the raspberry not speak the result
- `cardIndex = 1`
- `speakerName = "Speaker"`


# How to use

First start mycroft with
- `./start-mycroft.sh ...`

After the mycroft server is started start the python server with
- `python ./server-mycroft.py`

Now you can request to mycroft with:
- `http://xxxxx:8090/?speak=xxx_xxx&code=xxxx`
