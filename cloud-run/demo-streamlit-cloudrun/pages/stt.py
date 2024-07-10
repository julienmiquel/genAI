# Import packages
import speech_recognition as sr
import os
from gtts import gTTS
import datetime
import warnings
import calendar
import random
import wikipedia

# Ignore any warning messages
warnings.filterwarnings('ignore')


# Record audio and return as string
def recordAudio():
    # record the audio
    r = sr.Recognizer()  # creating a speech recogniser

    # open the mic and start recording
    with sr.Microphone() as source:
        print('Say Something:')
        audio = r.listen(source)
    # Use google speech recognition
    data = ''
    try:
        data = r.recognize_google(audio)
        print('You said : ' + data)
    except sr.UnknownValueError:
        print('Google Speech recognition not undstand you, unknown error')
    except sr.RequestError as e:
        print('Request results from google speechrecognition service error' + e)

    return data


recordAudio()


# A fuction to get the virtual assistant response
def assistantResponse(text):
    print(text)

    # convert the text to speech
    myobj = gTTS(text=text, lang='en', slow=False)

    # save the audio to a file
    myobj.save('assistant_response.mp3')

    # SPlay the converted file
    os.system('start assistant_response.mp3')


# A function for wake word
def wakeWord(text):
    WAKE_WORDS = {'hey bongo', 'hey man', 'hey computer', 'okay google'}  # list of wake words

    text = text.lower()  # convert the text to lower case words

    # Check to see if user input is a wake eord
    for phrase in WAKE_WORDS:
        if phrase in text:
            return True

    # If The wake word is not found in text from the loop , soo it returns False
    return False


# A function to get the current date
def getDate():
    now = datetime.datetime.now()
    my_date = datetime.datetime.today()
    weekday = calendar.day_name[my_date.weekday()]  # sunday
    monthNum = now.month
    dayNum = now.day

    # A list of months
    month_names = ['January', 'February', 'March', ' April', 'May', 'June', 'July', 'August', 'September', ' October',
                   'November', 'December']

    # A list of ordinal Numbers
    ordinalNumbers = ['1st', '2nd', '3rd', ' 4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th',
                      '14th', '15th', '16th',
                      '17th', '18th', '19th', '20th', '21st', '22nd', '23rd', '24rd', '25th', '26th', '27th', '28th',
                      '29th', '30th', '31st']

    return 'Today is ' + weekday + ' ' + month_names[monthNum - 1] + ' the ' + ordinalNumbers[dayNum - 1] + ' .'


# Fuction to return greeting
def greeting(text):
    # Greeting inputs
    GREETING_INPUTS = ['hi', 'hey', 'hola', 'wassup', 'hello']

    # Greeting response
    GREETING_RESPONSES = ['howdy', 'all that good', 'hello master', 'heythere']

    # If users input is a greeting, then return a randomly chosen greetng response
    for word in text.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES) + '.'

    # If no greeting was detected
    return ''


# A functions to get persons name from text
def getPerson(text):
    wordList = text.split()  # splits the text to words

    for i in range(0, len(wordList)):
        if i + 3 <= len(wordList) - 1 and wordList[i].lower() == 'who' and wordList[i + 1].lower() == 'is':
            return wordList[i + 2] + ' ' + wordList[i + 3]


while True:

    # record the audio
    text = recordAudio()
    response = ''

    # check for the wake word / phrase
    if (wakeWord(text) == True):

        # check for greetings by the user
        response = response + greeting(text)

        # check to see if the user has said anything about data
        if ('date' in text):
            get_date = getDate()
            response = response + ' ' + get_date

        # check to see if the user said 'who is'
        if ('who is' in text):
            person = getPerson(text)
            wiki = wikipedia.summary(person, sentences=2)
            response = response + ' ' + wiki

        # assistant respond back using audio and text from response
        assistantResponse(response)