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
from cachetools import LFUCache #pip install cachetools

# starterbot's ID as an environment variable
BOT_ID = 'U4J4KD6D6'
USER_NAME = None
EMOJI =None

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = ["do","list","help"]
GREETINGS_COMMAND = ["hi","hello","good even","good morn","hey","who", "good afternoon" "hey bot"]
HOW_COMMAND = ["how", "ok" ,"how r u"]

db = mysql.connector.connect(user='master', password='master123',
                              host='slackbotdb.cnobenweteje.us-west-1.rds.amazonaws.com',
                              database='slackbotdb')
cur = db.cursor()

where_list = []
select_list = []
query_word_list = []
bot_cache = LFUCache(maxsize=3) #Cache size 3

# instantiate Slack & Twilio clients
slack_client = SlackClient('xoxb-154155448448-dV0MCJdtWsGAcDJcE0c5hPyK')


def handle_command(command, channel):
    """Receives commands and returns response. """

    print 'handle_command :'+command
    #default response
    response = "Sorry!! The BOT won't handle this question yet :hushed:"
    if command in GREETINGS_COMMAND:
        print "GREETINGS_COMMAND"
        response = "Hello! "+USER_NAME+" This is Cmpe273 BOT"
        EMOJI = 'simple_smile'
        
    elif command in HOW_COMMAND:
        print "HOW_COMMAND"
        response = "I am good "+ USER_NAME+". How may I help you?"
        EMOJI = 'sunglasses'
        
    elif command == "thank" or command == "thank you":
        print "THANK"
        response = "Happy to help you!!"
        EMOJI = 'tada'

    else:
        EMOJI = 'point_left'
        generateQuery(command)
        if select_list and where_list:
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
            temp = ""
            for row in cur:
                for item in row:
                    print "--response-"+str(item)
                    if (len(row) > 1):
                        temp = " ,"    
                    response = response + str(item) + temp
                
    bot_cache[command] = response 
    slack_client.api_call("chat.postMessage", channel=channel,text=response+" :"+EMOJI+":", as_user=True)



def parse_slack_output(slack_rtm_output):

    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'],output['user']

    return None, None ,None

def generateQuery(command):
    del where_list[:]
    del select_list[:]
    if command.lower().startswith("when") : #user is asking for a DATE 
        print "-WHEN Clause--"
        if any(word in query_word_list for word in ['exam','mid','midterm','final']):
            where_list.append("TYPE = 'EXAM'")
            if any(word in query_word_list for word in ['mid','midterm']):
                where_list.append("SUB_TYPE = 'MID'")
            else:
                where_list.append("SUB_TYPE = 'FINAL'")
        
        if any(word in query_word_list for word in ['lab','lab1','lab2','lab3']):
            where_list.append("TYPE = 'LAB'")
            if any('1' in s for s in query_word_list):
                where_list.append("SUB_TYPE = '1'")
            elif any('2' in s for s in query_word_list):
                where_list.append("SUB_TYPE = '2'")
            elif any('3' in s for s in query_word_list):
                where_list.append("SUB_TYPE = '3'")
        elif any(word in query_word_list for word in ['assignment','assignment1','assignment2','assignment3','assign']):
            where_list.append("TYPE = 'ASSIGNMENT'")  
            if any('1' in s for s in query_word_list):
                where_list.append("SUB_TYPE = '1'")
            elif any('2' in s for s in query_word_list):
                where_list.append("SUB_TYPE = '2'")
            elif any('3' in s for s in query_word_list):
                where_list.append("SUB_TYPE = '3'")

        if any('due' in s for s in query_word_list):
            select_list.append('DUE_DATE')
        else :
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
        if any(word in query_word_list for word in ['weight' , 'weightag' , 'weightage']):
            where_list.append("TYPE = 'WEIGHTAGE'")
            if any('lab' in s for s in query_word_list):
                where_list.append("SUB_TYPE = 'LAB'")
            elif any('assign' in s for s in query_word_list):
                where_list.append("SUB_TYPE = 'ASSIGNMENT'")
            elif 'quiz' in query_word_list:
                where_list.append("SUB_TYPE = 'QUIZ'")
            elif 'project' in query_word_list:
                where_list.append("SUB_TYPE = 'PROJECT'")
            elif any('mid' in s for s in query_word_list):
                where_list.append("SUB_TYPE = 'MID'")
            elif any('final' in s for s in query_word_list):
                where_list.append("SUB_TYPE = 'FINAL'")
        elif 'cmpe' in query_word_list:
            where_list.append("TYPE = 'CMPE'")
            if '273' in query_word_list:
                where_list.append("SUB_TYPE = '273'")
        elif any('prof' in s for s in query_word_list):
            where_list.append("TYPE = 'PROFESSOR'")
            if 'email' in query_word_list:
                where_list.append("SUB_TYPE = 'EMAIL'")
        elif any('websit' in s for s in query_word_list):
            where_list.append("TYPE = 'WEBSITE'")
        elif any('prereq' in s for s in query_word_list):
            where_list.append("TYPE = 'PREREQUISITE'")
        elif any('coreq' in s for s in query_word_list):
            where_list.append("TYPE = 'COREQUISITE'")
        elif 'text' in query_word_list:
            where_list.append("TYPE = 'TEXT'")
            if 'book' in query_word_list:
                where_list.append("SUB_TYPE = 'BOOK'")
        select_list.append('ANSWER')
    
    
    #if command.startswith("Who") :
    elif command.startswith("who"):
        print "-WHO Clause--"
        del where_list[:]
        del select_list[:]
        if any(word in query_word_list for word in ['cmpe', '273', 'instructor' , 'professor','ta' ]):
            if any(word in query_word_list for word in ['instructor' , 'professor']):
                where_list.append("TYPE ='PROFESSOR'")
            elif 'ta' in query_word_list:
                where_list.append("TYPE ='TA'")
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

    elif command.startswith("which"):
        print "-WHICH Clause--"+command
        print query_word_list
        if any(word in query_word_list for word in ['cmpe', '273' ,'distribut', 'system' ]):
            print 'inside which'
            where_list.append("TYPE = 'DEPARTMENT'")
        select_list.append('ANSWER')

    if any(word in query_word_list for word in ['studi','materi']) :
        print "-GENERAL Clause--"
        del select_list[:]
        del where_list[:]
        where_list.append("TYPE = 'CMPE'")
        where_list.append("SUB_TYPE = '273'")
        select_list.append('ANSWER1')

    if 'object' in query_word_list:
        print "-OBJECTIVE Clause--"
        del select_list[:]
        del where_list[:]
        where_list.append("TYPE = 'OBJECTIVES'")
        select_list.append('ANSWER')
    if 'protocol' in query_word_list:
        print "-PROTOCOL Clause--"
        del select_list[:]
        del where_list[:]
        where_list.append("TYPE = 'PROTOCOL'")
        select_list.append('ANSWER')
    if any(word in query_word_list for word in ['time','hour']) :
        print "-hour Clause--"
        print query_word_list
        del select_list[:]
        del where_list[:]
        where_list.append("ANSWER = 'ENTERPRISE DISTRIBUTED SYSTEMS'")
        select_list.append('START_DATE')


def get_user_name(sc , user_id):
    api_call= sc.api_call("users.list")
    users = api_call.get('members')
    for user in users:
        for user in users:
            if 'name' in user and user.get('id') == user_id:
                print "user name is" + user['name']
                return user['name']


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("SJSU chatBOT connected and running!")
        bot_cache.clear() #Clear Cache
        stemmer = SnowballStemmer("porter")
        lmtzr = WordNetLemmatizer()
        stop_words= set(stopwords.words('english'))
        stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])
        while True:
            command, channel,user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                try :
                    USER_NAME = get_user_name(slack_client ,user)
                    print USER_NAME
                except ValueError:
                    print ValueError
                del where_list[:]
                del select_list[:]
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
                query_word_list = [s.strip('?') for s in query_word_list]
                for word in query_word_list:
                    command+=word+ " "
                print "---"+  command
                
                    

        # print "lemma sentence --:" +lemmaSentence
        # print "stemmer sentence --:" +Stemmer
        # print "command:" + command +" and channel:"+channel
        ##
                #compose_query(queryWordsList,channel)
        
                if(bot_cache.__contains__(command.strip())):
                    print "CACHE---"
                    slack_client.api_call("chat.postMessage", channel=channel,text=bot_cache[command.strip()], as_user=True)
                else:
                    handle_command(command.strip(), channel)
                time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
