from gtts import gTTS
import os

def say(text):
    # Say winning phrase out loud
    myobj = gTTS(text=text, lang='en', slow=False)
    # Saving the converted audio in a mp3 file named win
    myobj.save("win.mp3")
    # Playing the converted file
    os.system("afplay win.mp3")