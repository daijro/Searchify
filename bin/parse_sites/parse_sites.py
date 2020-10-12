import os
import sys
import json
from bs4 import BeautifulSoup
from parse import search
from requests_html import HTMLSession
from urllib.parse import urlencode
from Levenshtein import ratio as similar
import threading
import time
session = HTMLSession()

search_engine = None

total_elapsed_time = time.time()

search_term = sys.argv[1].strip()

newlist_links = []

def get_urls_google(search_term, site):
    global session, newlist_links, search_engine
    search_engine = 'Google'
    URL = f'https://google.com/search?{urlencode({"q": search_term+f" site:{site}.com"})}'
    data = session.get(URL).content
    soup = BeautifulSoup(data, "lxml")
    for link in [str(a.find('a')['href']).strip() for a in soup.find_all('div', class_='yuRUbf')]:
        #title = g.find('h3').text
        if 'quizlet.com' in link or 'brainly.com' in link:
            newlist_links.append(link)
    if newlist_links == []:
        get_urls_ddg(search_term, site)

def get_urls_ddg(search_term, site):
    global session, newlist_links, search_engine
    URL = f'https://duckduckgo.com/html/?{urlencode({"q": search_term+f" site:{site}.com", "t": "ffab", "atb": "v202-1", "ia": "web"})}'
    search_engine = 'DuckDuckGo'
    data = session.get(URL).content
    if data == b'If this error persists, please let us know: error-lite@duckduckgo.com':
        get_urls_bing(search_term, site)
    else:
        for link in [a.get('href') for a in BeautifulSoup(data, features="lxml").find_all('a', class_='result__url')]:
            link = link.strip()
            if 'quizlet.com' in link or 'brainly.com' in link:
                newlist_links.append(link)
        if newlist_links == []:
            get_urls_bing(search_term, site)

def get_urls_bing(search_term, site):
    global session, newlist_links, search_engine
    URL = f'https://bing.com/search?{urlencode({"q": search_term+f" site:{site}.com"})}'
    search_engine = 'Bing'
    data = session.get(URL).content
    soup = BeautifulSoup(data, "lxml")
    for g in soup.find_all('h2'):
        anchors = g.find_all('a')
        if anchors:
            link = anchors[0]['href']
            #title = g.find('h3').text
            if 'quizlet.com' in link or 'brainly.com' in link:
                newlist_links.append(link)
    if newlist_links == []:
        get_urls_yahoo(search_term, site)

def get_urls_yahoo(search_term, site):
    global session, newlist_links, search_engine
    URL = f'https://search.yahoo.com/search?{urlencode({"q": search_term+f" site:{site}.com"})}'
    search_engine = 'Yahoo'
    data = session.get(URL).content
    soup = BeautifulSoup(data, "lxml")
    for g in soup.find_all('a', class_="ac-algo fz-l ac-21th lh-24"):
        link = str(g['href'])
        if link.startswith('https://r.search.yahoo.com/'):
            link = str(BeautifulSoup(session.get(link).content).find('noscript'))[32:-37]
            if 'quizlet.com' in link or 'brainly.com' in link:
                newlist_links.append(link)
    if newlist_links == []:
        search_engine = None

try:
    search_threads = []
    if sys.argv[2] in ("quizlet.com", "quizlet.com,brainly.com"):
        search_threads.append(threading.Thread(target=get_urls_google, args=(search_term, 'quizlet')))
        search_threads[-1].daemon = True
        search_threads[-1].start()
    if sys.argv[2] in ("brainly.com", "quizlet.com,brainly.com"):
        search_threads.append(threading.Thread(target=get_urls_google, args=(search_term, 'brainly')))

        search_threads[-1].daemon = True
        search_threads[-1].start()
    for t in search_threads:
        t.join()
except:
    print(json.dumps({'output': [], 'error': 'There was an error parsing the google search. Please check your connection.', 'total_elapsed_time': time.time()-total_elapsed_time, 'search_engine': search_engine}))
    sys.exit()

if search_engine == None:
    print(json.dumps({'output': [], 'error': 'There was an error searching. You might be sending too many requests.', 'total_elapsed_time': time.time()-total_elapsed_time, 'search_engine': search_engine}))
    sys.exit()

if newlist_links == []:
    print(json.dumps({'output': [], 'error': 'Could not find any quizlet/brainly links on Google and DuckDuckGo. Please try again.', 'total_elapsed_time': time.time()-total_elapsed_time, 'search_engine': search_engine}))
    sys.exit()

newlist_links = list(dict.fromkeys(newlist_links))

def quizletparser(link):
    global all_results
    output = json.loads(os.popen(f'"{sys.argv[3]}" "quizlet" "{link}" "{search_term}"').read())
    all_results.append((output['confident'], output['answer'], output['question'], output['link'], output['elapsed_time']))

'''
def brainlyparser(link):
    global all_results
    output = json.loads(os.popen(f'"{os.path.join(os.path.dirname(sys.argv[0]), "parser_file.py")}" "brainly" "{link}" "{search_term}"').read())
    all_results.append((output['confident'], output['answer'], output['question'], output['link'], output['elapsed_time']))
'''

def brainlyparser(link):
    global all_results
    elapsed_time = time.time()
    data = BeautifulSoup(session.get(link).content, features="lxml")
    try:
        brainly_answer = json.loads(data.find_all('script')[10].string)['mainEntity']
        question = brainly_answer['name'].strip()
        for i in range(len(brainly_answer['suggestedAnswer'])):
            answer = brainly_answer['suggestedAnswer'][i]['text'].strip().replace('Answer:', 'Answer: ').replace('Explanation:', '\nExplanation: ')
            answer = answer + '\nThanks: '+str(brainly_answer['suggestedAnswer'][i]['upvoteCount'])
            confident = round(similar(search_term, question)*100, 2)
            all_results.append((confident, answer, question, link, time.time()-elapsed_time))
    except:
        try:
            brainly_answer = json.loads(data.find_all('script')[10].string)['mainEntity']
            question = brainly_answer['name'].strip()
            answer = brainly_answer['suggestedAnswer'][0]['text'].replace('Answer:', 'Answer: ').replace('Explanation:', '\nExplanation: ').strip()
            answer = answer + '\nThanks: '+str(brainly_answer['suggestedAnswer'][0]['upvoteCount'])
            confident = round(similar(search_term, question)*100, 2)
            all_results.append((confident, answer, question, link, time.time()-elapsed_time))
        except: pass


threads = []
all_results = []
output = {}


for j in range(len(newlist_links)):
    i = (j+1)*-1
    if newlist_links[i].startswith('https://quizlet.com'):
        threads.append(threading.Thread(target=quizletparser, args=(newlist_links[i],)))
        threads[-1].daemon = True
        threads[-1].start()
    if newlist_links[i].startswith('https://brainly.com'):
        threads.append(threading.Thread(target=brainlyparser, args=(newlist_links[i],)))
        threads[-1].daemon = True
        threads[-1].start()

for t in threads:
    t.join()
all_results.sort()

all_results = [dict(zip(['confidence', 'answer', 'question', 'link', 'elapsed_time'], x)) for x in all_results[::-1]]

if all_results == []:
    print(json.dumps({'output': all_results, 'error': 'Error, could not find any search results on the first page of Google.', 'total_elapsed_time': time.time()-total_elapsed_time, 'search_engine': search_engine}))
    sys.exit(0)

print(json.dumps({'output': all_results, 'error': 'Success', 'total_elapsed_time': time.time()-total_elapsed_time, 'search_engine': search_engine}))
sys.exit(0)