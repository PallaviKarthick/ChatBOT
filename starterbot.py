import os
import time
from slackclient import SlackClient
import string
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import string
import MySQLdb

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = ["do","list","help"]
GREETINGS_COMMAND = ["hi","hello","good evening","good morning","hey","who are you?", "good afternoon" "hey bot"]
HOW_COMMAND = ["how are you?","how are you doing?", "are you ok?"]
db = MySQLdb.connect("slackbotdb.cnobenweteje.us-west-1.rds.amazonaws.com","master","master123","slackbotdb" )
cur = db.cursor()
where_list = []
select_list = []
query_word_list = []

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

    if string.lower(str(command)) in GREETINGS_COMMAND:
        response = "Hello! This is SJSU Bot"
        
    if string.lower(str(command)) in HOW_COMMAND:
        response = "I am good. How may I help you?"            
        
    if string.lower(str(command))=="thanks" or string.lower(str(command))=="thank you":
        response = "Happy to help you!!"

    if command in EXAMPLE_COMMAND:
        if command.startswith("do"):
            response = "Do what ??"
        elif command.startswith("list"):
            response= "list of commands for you :\n" + ' '.join(EXAMPLE_COMMAND)
        else:
            response ="How can I help you?"

    else:
        generateQuery(command)
        select_string = select_list[0]
        where_string = where_list[0]
        for s in select_list[1:]:
            select_string += ","+s
        for w in where_list[1:]:
            where_string += "AND "+w
        query = "SELECT "+ select_string +" FROM course_details" + " WHERE "+where_string
        print query
        cur.execute(query)
        for row in cur.fetchall():
             response = str(row[0])


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

def generateQuery(command):
    del where_list[:]
    del select_list[:]
    if command.lower().startswith("when") : #user is asking for a DATE 
        if any(word in query_word_list for word in ['exam','mid','midterm','final']) :
            where_list.append("TYPE = 'EXAM'")
            if any(word in query_word_list for word in ['mid','midterm']):
                where_list.append("SUB_TYPE = 'MID'")
            else:
                where_list.append("SUB_TYPE = 'FINAL'")
        select_list.append('START_DATE')

    #if command.startswith("Where") :

    #if command.startswith("What") :
    
    #if command.startswith("Who") :




if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        
        stemmer = SnowballStemmer("english")
        lmtzr = WordNetLemmatizer()
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                word_list = command.lower().split(" ")
                #print word_list
                filtered_word_list = word_list[:]
                for word in word_list: # iterate over word_list
                    if word not in ["when","what", "where" ,"how","who"]:
                        if word in stopwords.words('english'):
                            filtered_word_list.remove(word)
                del query_word_list[:] #Clear query_word_list
                for word in filtered_word_list:
                    lemmaSentence = lmtzr.lemmatize(word)
                    query_word_list.append(lemmaSentence)
                print word_list

        # print "lemma sentence --:" +lemmaSentence
        # print "stemmer sentence --:" +Stemmer
        # print "command:" + command +" and channel:"+channel
        ##
                #compose_query(queryWordsList,channel)
                handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")





    
   
