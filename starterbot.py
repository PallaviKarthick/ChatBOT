import os
import time
from slackclient import SlackClient
import string
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import string
import mysql.connector

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = ["do","list","help"]
GREETINGS_COMMAND = ["hi","hello","good evening","good morning","hey","who are you?", "good afternoon" "hey bot"]
HOW_COMMAND = ["how are you?","how are you doing?", "are you ok?"]

db = mysql.connector.connect(user='master', password='master123',
                              host='slackbotdb.cnobenweteje.us-west-1.rds.amazonaws.com',
                              database='slackbotdb')
cur = db.cursor()

where_list = []
select_list = []
query_word_list = []

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """Receives commands and returns response. """

    print 'handle_command :'+command+":"
    if command in GREETINGS_COMMAND:
        print "GREETINGS_COMMAND"
        response = "Hello! This is SJSU Bot"
        
    elif command in HOW_COMMAND:
        print "HOW_COMMAND"
        response = "I am good. How may I help you?"            
        
    elif command == "thank" or command == "thank you":
        print "THANK"
        response = "Happy to help you!!"

    else:
        generateQuery(command)
        if select_list:
            select_string = select_list[0]
            where_string = where_list[0]
            for s in select_list[1:]:
                select_string += ","+s
            for w in where_list[1:]:
                where_string += "AND "+w
            query = "SELECT "+ select_string +" FROM course_details" + " WHERE "+where_string
            print query
            cur.execute(query)
            response=""
            for row in cur:
                for item in row:
                    print "--response-"+item
                    response = response + item +" ,"
       


    slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)



def parse_slack_output(slack_rtm_output):

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
        print "-WHEN Clause--"
        if any(word in query_word_list for word in ['exam','mid','midterm','final']) :
            where_list.append("TYPE = 'EXAM'")
            if any(word in query_word_list for word in ['mid','midterm']):
                where_list.append("SUB_TYPE = 'MID'")
            else:
                where_list.append("SUB_TYPE = 'FINAL'")
        select_list.append('START_DATE')

    #if command.startswith("Where") :
    elif command.startswith("where") :
        print "-WHERE Clause--"
        if any(word in query_word_list for word in ['class' or 'lecture' or 'classes' or 'lectures' ]):
            where_list.append("TYPE = 'LECTURE'")
            if 'Distributed Systems Overview' in query_word_list:
                where_list.append("SUB_TYPE = 'Distributed Systems Overview'")
            if 'Remote Procedural Calls' in query_word_list:
                where_list.append("SUB_TYPE = 'Remote Procedural Calls'") 
            if 'messaging' in query_word_list:
                where_list.append("SUB_TYPE = 'Messaging'")
        elif 'exam' in query_word_list:
            where_list.append("TYPE = 'EXAM'")
            if 'mid' in query_word_list:
                where_list.append("SUB_TYPE = 'MID'")
            else :
                where_list.append("SUB_TYPE = 'FINAL'")
        select_list.append('LOCATION')

    #if command.startswith("What") :
    elif command.startswith("what"):
        print "-WHAT Clause--"
        if 'weightage' in query_word_list:
            where_list.append("TYPE = 'WEIGHTAGE'")
            if 'lab' in query_word_list:
                where_list.append("SUB_TYPE = 'LAB'")
            elif 'assignment' in query_word_list:
                where_list.append("SUB_TYPE = 'ASSIGNMENT'")
            elif 'quiz' in query_word_list:
                where_list.append("SUB_TYPE = 'QUIZ'")
            elif 'project' in query_word_list:
                where_list.append("SUB_TYPE = 'PROJECT'")
            elif 'midterm' in query_word_list:
                where_list.append("SUB_TYPE = 'MID'")
            elif 'final' in query_word_list:
                where_list.append("SUB_TYPE = 'FINAL'")
        elif 'cmpe' in query_word_list:
            where_list.append("TYPE = 'CMPE'")
            if '273' in query_word_list:
                where_list.append("SUB_TYPE = '273'")
        elif 'website' in query_word_list:
            where_list.append("TYPE = 'WEBSITE'")
        elif 'prerequisite' in query_word_list:
            where_list.append("TYPE = 'PREREQUISITE'")
        select_list.append('ANSWER')
    
    
    
    #if command.startswith("Who") :
    elif command.startswith("who"):
        print "-WHO Clause--"
        if 'cmpe' in query_word_list or '273' in query_word_list:
            where_list.append("TYPE = 'CMPE'")
            if 'instructor' in query_word_list:
                where_list.append("SUB_TYPE ='INSTRUCTOR'")
            elif 'ta' in query_word_list:
                where_list.append("SUB_TYPE ='TA'")
        elif 'grade' in query_word_list :
            where_list.append("TYPE = 'GRADE'")
            if 'final' in query_word_list or 'project' in query_word_list:
                where_list.append("SUB_TYPE='finals'")
        select_list.append('ANSWER')

    elif command.startswith("how"):
        print "-HOW Clause--"
        if 'grade' in query_word_list:
            where_list.append("TYPE = 'GRADE'")
            if 'project' in query_word_list:
                where_list.append("SUB_TYPE = 'PROJECTS'")
            elif 'final' in query_word_list:
                where_list.append("SUB_TYPE = 'FINALS'")
        select_list.append('WEIGHT')

    if any(word in query_word_list for word in ['studi','materi']) :
        print "-GENERAL Clause--"
        del select_list[:]
        where_list.append("TYPE = 'CMPE'")
        where_list.append("SUB_TYPE = '273'")
        select_list.append('STUDY_LINKS')

    if 'object' in query_word_list:
        print "-OBJECTIVE Clause--"
        del select_list[:]
        where_list.append("TYPE = 'OBJECTIVES'")
        select_list.append('ANSWER')
    if 'protocol' in query_word_list:
        print "-PROTOCOL Clause--"
        del select_list[:]
        where_list.append("TYPE = 'PROTOCOL'")
        select_list.append('ANSWER')
           
            
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        
        stemmer = SnowballStemmer("porter")
        lmtzr = WordNetLemmatizer()
        stop_words= set(stopwords.words('english'))
        stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                word_list = command.lower().split(" ")
                #print word_list
                filtered_word_list = word_list[:]
                for word in word_list: # iterate over word_list
                    if word not in ["when","what", "where" ,"how","who","which"]:
                        if word in stop_words:
                            filtered_word_list.remove(word)
                del query_word_list[:] #Clear query_word_list
                for word in filtered_word_list:
                    lemmaSentence = lmtzr.lemmatize(word)
                    stm_word= stemmer.stem(lemmaSentence)
                    print stm_word
                    query_word_list.append(stm_word)
                command=""
                for word in query_word_list:
                    command+=word+ " "
                print command
                    

        # print "lemma sentence --:" +lemmaSentence
        # print "stemmer sentence --:" +Stemmer
        # print "command:" + command +" and channel:"+channel
        ##
                #compose_query(queryWordsList,channel)
        
                handle_command(command.strip(), channel)
                time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")





    
   
