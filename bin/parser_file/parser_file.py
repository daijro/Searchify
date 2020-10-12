import sys
import json
from Levenshtein import ratio as similar
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import time
session = HTMLSession()

def quizletparser(link):
    elapsed_time = time.time()
    try:
        content = session.get(link).content
        data = BeautifulSoup(content, features="lxml")
        quizlet_data = list(json.loads(data.find_all('script')[-6].string[:-152][44:])['termIdToTermsMap'].values())
        questions = [elem["word"] for elem in quizlet_data]
        answers = [elem["definition"] for elem in quizlet_data]

        #zipped = list(zip([similar(sys.argv[3], x) for x in questions], questions, answers)) + list(zip([similar(sys.argv[3], x) for x in answers], answers, questions))
        zipped = max(list(zip([similar(sys.argv[3], x) for x in questions], questions, answers)))

        question = zipped[1].strip()
        confident = round(zipped[0]*100, 2)
        answer = zipped[2].strip()
        return json.dumps({'confident': confident, 'answer': answer, 'question': question, 'link': link, 'elapsed_time': time.time()-elapsed_time})
    except: sys.exit()

def brainlyparser(link):
    import re
    elapsed_time = time.time()
    data = BeautifulSoup(session.get(link).content, features="lxml")
    try:
        brainly_answer = json.loads(data.find_all('script')[10].string)['mainEntity']
        question = brainly_answer['name'].strip()
        for i in range(len(brainly_answer['suggestedAnswer'])):
            answer = brainly_answer['suggestedAnswer'][i]['text'].strip().replace('Answer:', 'Answer: ').replace('Explanation:', '\nExplanation: ')
            answer = answer + '\nThanks: '+str(brainly_answer['suggestedAnswer'][i]['upvoteCount'])
            confident = round(similar(sys.argv[3], question)*100, 2)
            #all_results.append((confident, answer, question, link, time.time()-elapsed_time))
            return json.dumps({'confident': confident, 'answer': re.sub("[\[].*?[\]]", "", answer).strip(), 'question': question, 'link': link, 'elapsed_time': time.time()-elapsed_time})
    except:
        try:
            brainly_answer = json.loads(data.find_all('script')[10].string)['mainEntity']
            question = brainly_answer['name'].strip()
            answer = brainly_answer['suggestedAnswer'][0]['text'].replace('Answer:', 'Answer: ').replace('Explanation:', '\nExplanation: ').strip()
            answer = answer + '\nThanks: '+str(brainly_answer['suggestedAnswer'][0]['upvoteCount'])
            confident = round(similar(sys.argv[3], question)*100, 2)
            #all_results.append((confident, answer, question, link, time.time()-elapsed_time))
            return json.dumps({'confident': confident, 'answer': re.sub("[\[].*?[\]]", "", answer).strip(), 'question': question, 'link': link, 'elapsed_time': time.time()-elapsed_time})
        except: sys.exit()

if sys.argv[1] == "brainly":
    print(brainlyparser(sys.argv[2]))
    sys.exit()
if sys.argv[1] == "quizlet":
    print(quizletparser(sys.argv[2]))
    sys.exit()