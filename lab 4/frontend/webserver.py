###################csc326 lab2 frontend #######################
######################2016-10-21###################
######################Wang Jiayiang###############

import bottle, httplib2, beaker, oauth2client, sqlite3
from bottle import get,request,post
from bottle import route, run
from bottle import template
from bottle import error
from bottle import PasteServer
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware
from autocorrect import spell
from mathtest import BNF, pushFirst,pushUMinus,evaluateStack,mathresult
from plot import string2func,myplotfunc
mathstr=False
mathplot=False
##############Anonymous Mode###########################
#####search history disable######################
#############Signed-in Mode######################
##your application should handle such information is not available
###sugn-out bbutton must be provided on every page of the website
###At least 10 most recenrly search  words by the user should be stored
###########create a history list to hold all keywords searched#########
history_list={}
login = False


client_id = '658889954882-7metdvahvejlrfk3vq0d09v7mingqfro.apps.googleusercontent.com'
client_secret = 'clxf_Q-1G557-LvHWahMIId3'
session_opts = {
     'session.type': 'file',
     'session.cookie_expires': 300,
     'session.data_dir': './data',
     'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)

############### random list of url ###############

url_list = []
url_list_dict = {}
url_list_dict_sorted = {}

########Homepae contains the input box and the history table##########
@get('/')
def keywords():
    global mykeyword, url_list, url_list_dict_sorted, Google_Search_Name,mathplot,mathstr
    global original_my_words, Original_Google_Search_Name
    session = request.environ.get('beaker.session')
    session.save()
    mykeyword = request.query.keywords
    #####get user input#####

    mathstr = False
    mykeywordformath = mykeyword.replace(" ", "")
    mymathstr = mathresult(mykeyword)
    if mymathstr:
        mathstr = True
        if login:
            email = session['user']
            pic = session['picture']
            name = session['name']

            if url_list == -1:
                return template('error_page_search.html', email=session['user'], pic=pic, name=name, login=login)
            else:
                return template('calresult.html', val=mymathstr, SearchFor=mykeywordformath, email=email, pic=pic, name=name,
                                login=login, url_list=url_list)
        else:
            if url_list == -1:
                return template('error_page_search.html', email=None, pic=None, name=None, login=False)
            else:
                return template('calresult.html', val=mymathstr, SearchFor=mykeywordformath, email=None, pic=None, name=None,
                                login=login, url_list=url_list)

    mathfunc = False
    mathfunc = myplotfunc(mykeyword)
    if mathfunc and mathstr == False:
        mathplot = True

        if login:
            email = session['user']
            pic = session['picture']
            print "PIC IS " + str(pic)
            name = session['name']
            if url_list == -1:
                return template('error_page_search.html', email=session['user'], pic=pic, name=name, login=login)
            else:
                return template('finalplot.html', val=mykeyword, email=email, pic=pic,
                                name=name,
                                login=login, url_list=url_list)
        else:
            if url_list == -1:
                return template('error_page_search.html', email=None, pic=None, name=None, login=False)
            else:
                return template('finalplot.html', val=mykeyword, email=None, pic=None,
                                name=None,
                                login=login, url_list=url_list)

    if mykeyword and mathstr == False and mathfunc == False:
        (my_words, word_list, mykeyword, word_count) = get_keywords()
        if login:
            email = session['user']
            pic = session['picture']
            name = session['name']
            if url_list == []:
                return template('error_page_search.html',email=session['user'], pic=pic, name=name, login=login,\
                                mykeyword=mykeyword, Google_Search_Name=Google_Search_Name,\
                                word_temp=original_my_words, Original_Google_Search_Name=Original_Google_Search_Name)
            else:
                return template('results.html', rows=word_list, crows=my_words, SearchFor=mykeyword,word_count=word_count,\
                                email=email, pic=pic, name=name, login=login, url_list=url_list, mykeyword=mykeyword,\
                                Google_Search_Name=Google_Search_Name, word_temp=original_my_words, \
                                Original_Google_Search_Name=Original_Google_Search_Name)
        else:
            if url_list == []:
                return template('error_page_search.html',email=None, pic=None, name=None, login=False,\
                                mykeyword=mykeyword, Google_Search_Name=Google_Search_Name, \
                                word_temp=original_my_words, Original_Google_Search_Name=Original_Google_Search_Name)
            else:
                return template('results.html', rows=word_list, crows=my_words, SearchFor=mykeyword,word_count=word_count,\
                                email=None, pic=None, name=None, login=login, url_list=url_list, mykeyword=mykeyword,\
                                Google_Search_Name=Google_Search_Name, word_temp=original_my_words, \
                                Original_Google_Search_Name=Original_Google_Search_Name)


    else:
        ######user opens the website for the first time#########
        if login:
                current_list = []
                print history_list

                try:
                  user_name = session['user']
                  pic = session['picture']
                  name = session['name']

                except:
                  return template('searchpage_notable.html',history = history_list, email=None, pic=None, name=None, login=login)

                print session
                current_list = []
                print history_list
                current_list = history_list[user_name]
                return template('searchpage_table.html',history = current_list, email=session['user'], pic=pic, name=name, login=login)
        else:
                return template('searchpage_notable.html',history = history_list, email=None, pic=None, name=None, login=login)


def get_keywords():
########################count the words############################
        global url_list, url_list_dict_sorted, url_list_dict, Google_Search_Name, mykeyword
        global original_my_words, Original_Google_Search_Name, original_url_link
        del url_list[:]
        url_list_dict_sorted = []
        original_url_link = []
        my_string = mykeyword
        my_words = my_string.split()
        original_my_words_copy = my_words
        original_my_words_copy = [word.lower() for word in original_my_words_copy]
        original_my_words = " ".join(original_my_words_copy)
        my_words = [spell(word) for word in my_words]
        my_words = [upper.lower() for upper in my_words]
        mykeyword = ' '.join(my_words)
        word_temp = my_string.split()  # copy
        word_temp = [upper2.lower() for upper2 in word_temp]

        for i in range(len(original_my_words_copy)):
            Original_Google_Search_Name = "+".join(original_my_words_copy)
        for i in range(len(my_words)):
            url_list_temp = search_word("lab3.db", my_words[i])
            url_list = []
            Google_Search_Name = "+".join(my_words)
        for i in range(len(url_list_dict_sorted)):
            link, time = url_list_dict_sorted[i]
            url_list.append(link)
        url_list_dict_sorted = []
        url_list_dict.clear()

        if login:
            session = bottle.request.environ.get('beaker.session')
            session.save()

            if session['user']:
                user_name=session['user']
                pic = session['picture']
                name = session['name']

            if user_name not in history_list:
                history_list[user_name]=[]
                for word in my_words:
                    history_list[user_name].insert(0, word)
            else:
                current_list=[]
                current_list=history_list[user_name]
                for word in my_words:
                       current_list.insert(0,word)


        count = len(my_words)
        word_list=[]   #####store the keywords########


        ##########################################################################
        for i in range(count):
            word = word_temp[i]
            time = 0
            for x in range(count):

                if word == "":
                    x += 1

                elif x == count - 1:
                    if word == my_words[count - 1]:
                        time += 1
                        word_temp[x] = ""
                    word_list.append(word)
                    word_count=len(word_list)

                elif word == word_temp[x]:
                    time += 1
                    word_temp[x] = ""
                    x += 1

                else:
                    x += 1

        return (my_words,word_list,mykeyword,word_count)


google_scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'
google_redirect_uri = 'http://localhost:8070/oauth2callback'
#google_redirect_uri = 'http://127.0.0.1/oauth2callback'
#google_redirect_uri = 'http://ec2-54-81-54-127.compute-1.amazonaws.com/oauth2callback'
client_id = '909426871264-62t0ough11e5m617k1o2v7244me9natg.apps.googleusercontent.com'
client_secret = 'YpTt8kWT_r6t_CPiuQeUbxpP'


# Function to find urls associated with search word.
# Fucntion sorts the urls by page rank
# Returns -1 if no results were found, a list of url strings otherwise
def search_word(database, word):
    global url_list_dict_sorted, url_list_dict
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # First need to find the word id of the search word, will use the lexicon
    c.execute("SELECT word_id from lexicon where word = '%s'" % word)
    word_id = c.fetchone()
    if word_id:
        word_id = word_id[0]

    else:
        return -1

    # Second, we find the doc_ids that feature this word using the inverted_index
    c.execute("SELECT doc_ids from invertedIndex where word_id = '%d'" % word_id)
    doc_ids = c.fetchone()[0]

    # Third, we extract each doc_id into a list:
    doc_ids_list = doc_ids.split(",")
    doc_ids_list = [int(x) for x in doc_ids_list]

    # Fourth, we extract the page ranks of each link to sort the final list of results
    ranks = []
    for doc_id in doc_ids_list:
        c.execute("SELECT rank from pageRank where doc_id = '%d'" % doc_id)
        rank = c.fetchone()[0]
        ranks.append(rank)

    sorted_doc_list = zip(ranks, doc_ids_list)
    sorted_doc_list.sort(reverse=True)
    sorted_doc_list = [doc_id for x, doc_id in sorted_doc_list]


    # Fifth, we extract urls for doc_ids we got:
    urls = []

    for doc in sorted_doc_list:
        status = c.execute("SELECT url from document where doc_id = '%d'" % doc)        
        url = c.fetchone()[0]
        #urls.append(url)
        status = c.execute("SELECT title from document where url = '%s'" % url)
        title = c.fetchone()[0]
        print title
        urls.append((title, url))
    print urls # [(title, url)]
    for i in range(len(urls)):
        if urls[i] not in url_list_dict:
            url_list_dict[urls[i]] = 1
        else:
            url_list_dict[urls[i]] += 1
    url_list_dict_sorted = sorted(url_list_dict.items(), key=lambda x:x[1], reverse=True)
    print url_list_dict_sorted
    return url_list_dict_sorted

@route('/login')
def home_login():
    global login, url_list
    login = True
    status=False
    session = request.environ.get('beaker.session')
    session.save()
    if not history_list:
        session.clear()

    if session.get('user',None) is None :

        flow = flow_from_clientsecrets("client_secret.json", scope=google_scope, redirect_uri=google_redirect_uri)
        uri = flow.step1_get_authorize_url()
        bottle.redirect(str(uri))
    else:
        user_name = session['user']
        pic = session['picture']
        name = session['name']
        current_list = []
        current_list = history_list[user_name]
        if current_list == None:
            return template('searchpage_notable.html', email=user_name, pic=pic, name=name, login=login)
        else:
            return template('searchpage_table.html', history = current_list, email=user_name, pic=pic, name=name, login=login)


@route('/logout')
def logout():
    session = bottle.request.environ.get('beaker.session')
    session['user'] = ''
    session['picture'] = ''
    session['name'] = ''
    login = False
    session.clear()
    session.save()

    #bottle.redirect("https://www.google.com/accounts/Logout?continue=https://appengine.google.com/_ah/logout?continue=http://localhost:8070/logout/redirect")
    bottle.redirect("http://localhost:8070/logout/redirect")
    #bottle.redirect("http://ec2-54-81-54-127.compute-1.amazonaws.com/logout/redirect")


    return template('searchpage_notable.html', email=session['user'], pic=session['picture'], name=session['name'], login=login)


@route('/logout/redirect')
def logout_redirect():

    session = bottle.request.environ.get('beaker.session')
    session['user'] = None
    session['picture'] = None
    session['name'] = None
    global login, url_list
    login = False
    return template('searchpage_notable.html', email=session['user'], pic=session['picture'], name=session['name'], login=login)

@route('/oauth2callback')
def redirect_page():
      global url_list
      code = request.query.get('code','')
      flow = OAuth2WebServerFlow (client_id = client_id,
                                  client_secret = client_secret,
                                  scope = google_scope,
                                  redirect_uri = google_redirect_uri)
      credentials = flow.step2_exchange(code)
      token = credentials.id_token['sub']

      http = httplib2.Http()
      http = credentials.authorize(http)
      users_service =  build('oauth2','v2', http=http)
      user_document = users_service.userinfo().get().execute()
      user_email = user_document['email']
      session = request.environ.get('beaker.session')
      session['user'] = user_document['email']
      session['picture'] = user_document['picture']
      session['name'] = user_document['name']
      session.save()
      user_name=session['user']
      pic=session['picture']
      name = session['name']
      if not history_list:
          return template('searchpage_notable.html', email=session['user'], pic=pic, name=name, login=login)
      else:
          user_name = session['user']
          pic = session['picture']
          name = session['name']
          if user_name not in history_list:
              return template('searchpage_notable.html', email=session['user'], pic=pic, name=name, login=login)
          else:
              print history_list
              current_list = []
              current_list = history_list[user_name]
              return template('searchpage_table.html', history=current_list, email=session['user'], pic=pic, name=name, login=login)


@get('/testing')
def testing():
    return template('test.html')

@error(404)
def error_page(error):
    session = request.environ.get('beaker.session')
    session.save()
    if login:

        email = session['user']
        pic = session['picture']
        name = session['name']
        return template('error_page_404.html',email=email, pic=pic,name=name, login=True)

    else:
         return template('error_page_404.html',email=None, pic=None,name=None, login=False)

## Run the webserver at localhost on port 8080
run(host='localhost',port=8070,debug=True,app=app)
#run(server=PasteServer, host='0.0.0.0', port=80, debug=True, app=app)