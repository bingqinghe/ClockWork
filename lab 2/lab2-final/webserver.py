###################csc326 lab2 frontend #######################
######################2016-10-21###################
######################Wang Jiayiang###############

import bottle, httplib2, beaker, oauth2client
from bottle import get,request,post
from bottle import route, run
from bottle import template
from bottle import PasteServer
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware
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

########Homepae contains the input box and the history table##########
@get('/')
def keywords():
    global mykeyword
    session = request.environ.get('beaker.session')
    session.save()

    #####get user input#####
    mykeyword = request.query.keywords
    print mykeyword
    if mykeyword:
        (my_words, word_list, mykeyword, word_count) = get_keywords()
        if login:
            email = session['user']
            pic = session['picture']
            print "PIC IS " + str(pic)
            name = session['name']
            return template('results.html', rows=word_list, crows=my_words, SearchFor=mykeyword,word_count=word_count,email=email, pic=pic, name=name, login=login)
        else:

            return template('results.html', rows=word_list, crows=my_words, SearchFor=mykeyword,word_count=word_count,email=None, pic=None, name=None, login=login)


    else:
        ######user opens the website for the first time#########
       # if not history_list:
        #    history_exist = True
         #   if login:
          #      return template('searchpage_notable.html', email=session['user'], login=login)
           # else:
            #    return template('searchpage_notable.html', email=None, login=login)
        #else:
        if login:
                print "was here"
                user_name = session['user']
                pic = session['picture']
                print "PIC IS " + str(pic)
                name = session['name']

                print session
                current_list = []
                print history_list
                current_list = history_list[user_name]
                return template('searchpage_table.html',history = current_list, email=session['user'], pic=pic, name=name, login=login)
        else:
                print ("hihhi")
                return template('searchpage_notable.html',history = history_list, email=None, pic=None, name=None, login=login)


def get_keywords():
########################count the words############################
        my_string = mykeyword
        my_words = my_string.split()
        my_words = [upper.lower() for upper in my_words]
        word_temp = my_string.split()  # copy
        word_temp = [upper2.lower() for upper2 in word_temp]


        if login:
            print login
            session = bottle.request.environ.get('beaker.session')
            session.save()
            print session

           # print history_list
            if session['user']:
                user_name=session['user']
                pic = session['picture']
                print "PIC IS " + str(pic)
                name = session['name']
           # print history_list
            if user_name not in history_list:
                history_list[user_name]=[]
                print ("in")
                for word in my_words:
                    history_list[user_name].insert(0, word)
                   # print history_list[name]
                   # print history_list]
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
google_redirect_uri = 'http://ec2-52-55-236-247.compute-1.amazonaws.com/oauth2callback'
#google_redirect_uri = 'http://127.0.0.1/oauth2callback'
client_id = '909426871264-62t0ough11e5m617k1o2v7244me9natg.apps.googleusercontent.com'
client_secret = 'YpTt8kWT_r6t_CPiuQeUbxpP'
@route('/login')
def home_login():
    global login
    login = True
    status=False
    ## print "test"
    #print login
    session = request.environ.get('beaker.session')
    session.save()
    print history_list
    if not history_list:
        session.clear()

    print session
    if session.get('user',None) is None :
        print ("debug login first time")
        print session
        flow = flow_from_clientsecrets("client_secret.json", scope=google_scope, redirect_uri=google_redirect_uri)
        uri = flow.step1_get_authorize_url()
        bottle.redirect(str(uri))
    else:
    	print "Second login, no need for permissions."
        print ("debug login second time")
        user_name = session['user']
        pic = session['picture']
        print "PIC IS " + str(pic)
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
    #print session

    # bottle.redirect("https://www.google.com/accounts/Logout?continue=https://appengine.google.com/_ah/logout?continue=http://http://ec2-52-70-225-223.compute-1.amazonaws.com/logout/redirect")
    # bottle.redirect("http://127.0.0.1/logout/redirect")
    bottle.redirect("http://ec2-52-55-236-247.compute-1.amazonaws.com/logout/redirect")


    return template('searchpage_notable.html', email=session['user'], pic=session['picture'], name=session['name'], login=login)


@route('/logout/redirect')
def logout_redirect():

    session = bottle.request.environ.get('beaker.session')
    session['user'] = None
    session['picture'] = None
    session['name'] = None
    global login
    login = False
    return template('searchpage_notable.html', email=session['user'], pic=session['picture'], name=session['name'], login=login)

@route('/oauth2callback')
def redirect_page():
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
     # print user_document
      user_email = user_document['email']
      session = request.environ.get('beaker.session')
      session['user'] = user_document['email']
      session['picture'] = user_document['picture']
      session['name'] = user_document['name']
      print user_document
      #print session['user']
      session.save()
      user_name=session['user']
      pic=session['picture']
      print "PIC IS " + str(pic)
      name = session['name']
      print pic
      if not history_list:
          print "jou"
          return template('searchpage_notable.html', email=session['user'], pic=pic, name=name, login=login)
          #return template('ss.html', email=session['user'], pic=pic,login=login)
      else:

          print "jou2"
          print session
          user_name = session['user']
          pic = session['picture']
          print "PIC IS " + str(pic)
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

## Run the webserver at localhost on port 8080
run(server=PasteServer, host='0.0.0.0',port=80,debug=True,app=app)
