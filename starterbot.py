import os
import time
from slackclient import SlackClient
import string
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import string

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = ["do","list","help"]

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
        """
    response = "Not sure what you mean. Use the *" + ' '.join(EXAMPLE_COMMAND) + \
        "* command with numbers, delimited by spaces."
    if command in EXAMPLE_COMMAND:
        if command.startswith("do"):
            response = "Do what ??"
        elif command.startswith("list"):
            response= "list of commands for you :\n" + ' '.join(EXAMPLE_COMMAND)
        else:
            response ="Happy to help you!!"



    slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
        """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                    output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        
        stemmer = SnowballStemmer("english")
        lmtzr = WordNetLemmatizer()
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                word_list = command.split(" ")
                #print word_list
                filtered_word_list = word_list[:]
                for word in word_list: # iterate over word_list
                    if word in stopwords.words('english'):
                        filtered_word_list.remove(word)
                #print filtered_word_list
                
                for word in filtered_word_list:
                    ##print " -word-- :"+word
                    lemmaSentence = lmtzr.lemmatize(word)
                    
                    print lemmaSentence
        
        
        
        
        
        
        # print "lemma sentence --:" +lemmaSentence
        # print "stemmer sentence --:" +Stemmer
        # print "command:" + command +" and channel:"+channel
                handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")