# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
import sqlite3
from pagerank import page_rank

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        
        # Document Index/Lexicon: Memory and Database
        self._conn = sqlite3.connect("lab4.db")
        self._cursor = self._conn.cursor()

        # lists of dicts
        self._doc_index = [ ]
        self._lexicon = [ ]
        self._links = [ ]

        # dict
        self._inverted_index = { }

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
        def create_tables(self):
            # Document index
            self._cursor.execute('''CREATE TABLE IF NOT EXISTS document (doc_id integer primary key, url text not null unique, title text, alt text, url_text text)''') #title text, description text)''')
            self._cursor.execute('''CREATE TABLE IF NOT EXISTS lexicon (word_id integer primary key, word text not null unique)''')
            self._cursor.execute('''CREATE TABLE IF NOT EXISTS links (from_doc_id integer not null, to_doc_id integer not null)''')
            self._cursor.execute('''CREATE TABLE IF NOT EXISTS invertedIndex (word_id integer not null unique, doc_ids text not null)''')
            self._cursor.execute('''CREATE TABLE IF NOT EXISTS pageRank (doc_id integer not null unique, rank real)''')            
            
        create_tables(self)

    # TODO remove me in real version
    # def _mock_insert_document(self, url):
    #     """A function that pretends to insert a url into a document db table
    #     and then returns that newly inserted document's id."""
    #     ret_id = self._mock_next_doc_id
    #     self._mock_next_doc_id += 1
    #     return ret_id

    # Insert a url into the document tb table, return the inserted doc's id
    def insert_document(self, url):
        
        self.calculate_pagerank()


        # # Database code:
        vals = (None, str(url), None, None, None)
        self._cursor.execute("INSERT OR IGNORE INTO document VALUES (?,?,?,?,?)", vals)

        print url
        self._cursor.execute("SELECT doc_id FROM document WHERE url = '%s'" % url)
        self._conn.commit()

        ret_id = self._cursor.fetchone()[0]    
        
        ret_id = -1

        # Memory code:
        doc = {'doc_id': self._mock_next_doc_id, 'url': url}
        exists = False
        for docs in self._doc_index:
            if docs['url'] == url:
                exists = True  # link already visited, no need to append the url
                print "Link already visited" 
                ret_id = docs['doc_id']   
        
        if exists == False:
            self._doc_index.append(doc)

            ret_id = self._mock_next_doc_id
            self._mock_next_doc_id += 1

        return ret_id

    # # TODO remove me in real version
    # def _mock_insert_word(self, word):
    #     """A function that pretends to inster a word into the lexicon db table
    #     and then returns that newly inserted word's id."""
    #     ret_id = self._mock_next_word_id
    #     self._mock_next_word_id += 1
    #     return ret_id
    
    #Insert a word into the lexicon tb table, return the inserted word's id
    def insert_word(self, word):
        
        # # Database code:
        vals = (None, str(word))
        self._cursor.execute("INSERT OR IGNORE INTO lexicon VALUES (?,?)", vals)

        self._cursor.execute("SELECT word_id FROM lexicon WHERE word = '%s'" % word)
        self._conn.commit()

        # ret_id = self._cursor.fetchone()[0] 
        
        # Memory code:
        lex = {'word_id': self._mock_next_word_id, 'word': word}
        exists = False
        for words in self._lexicon:
            if words['word'] == word:
                exists = True 
                # print "Word already seen" (need to add the doc id to the inverted index)
                ret_id = words['word_id'] 
                self._inverted_index[ret_id].update([self._curr_doc_id])

        
        if exists == False:
            self._lexicon.append(lex)
            ret_id = self._mock_next_word_id
            self._inverted_index[ret_id] = set([self._curr_doc_id])
            self._mock_next_word_id += 1

        return ret_id

    def insert_inverted_index(self):
        for word_id, doc_ids in self._inverted_index.iteritems():
            
            vals = (word_id, ','.join(str(docid) for docid in doc_ids))            
            self._cursor.execute("INSERT OR IGNORE INTO invertedIndex VALUES (?,?)", vals)
            self._conn.commit()

    def calculate_pagerank(self):
        
        ranks = page_rank(self._links)

        for doc_id, rank in ranks.iteritems():
            
            vals = (doc_id, rank)
            self._cursor.execute("INSERT OR IGNORE  INTO pageRank VALUES (?, ?)", vals)
            self._conn.commit()


    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            word_id = self._word_id_cache[word]
        
        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word, 
        #          store it in the word id cache, and return the id.

        word_id = self.insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        # TODO: just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.
        
        doc_id = self.insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # TODO

        # memory (cache)
        self._links.append((from_doc_id, to_doc_id))

        # db
        vals = (from_doc_id, to_doc_id)

        self._cursor.execute("INSERT INTO links VALUES (?,?)", vals)        
        self._conn.commit()

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print "document title="+ repr(title_text)

        # TODO update document title for document id self._curr_doc_id

        # Memory:
        self._doc_index[self._curr_doc_id-1]['title'] = title_text

        # # # Database:
        self._cursor.execute("UPDATE document SET title=? WHERE doc_id=?", (title_text, self._curr_doc_id))
        self._conn.commit()

        
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        # print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        
        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url
        # # # Database:
        self._cursor.execute("UPDATE document SET title=?, alt=?, url_text=? WHERE doc_id=?", (repr(attr(elem,"title")), repr(attr(elem,"alt")), repr(attr(elem,"text")), self._curr_url))
        self._conn.commit()
    
    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        print "    num words="+ str(len(self._curr_words))

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            try:
                doc_id = self.document_id(url)
            except:
                continue

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())
                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()

        self.insert_inverted_index()
        self.calculate_pagerank()

    # return the inverted index which contains the word ids and doc ids 
    def get_inverted_index(self):
        # return the inverted index in a dict()
        return self._inverted_index

    # return the resolved index which contains the words themselves as well as the urls
    def get_resolved_inverted_index(self):
        # return the resolved inverted index in a dict()
        resolved_inverted_index = { }
        # for each word id
        for word in self._inverted_index:
            doc_urls = []

            # navigate the set of doc ids for this word id and append it to a list
            for doc_id in self._inverted_index[word]:
                doc_urls.append(self._doc_index[doc_id-1]['url'])
            # print doc_urls

            resolved_inverted_index[self._lexicon[word-1]['word']] = set(doc_urls)

        return resolved_inverted_index
        # print resolved_inverted_index



    # Identical to crawl but needed to modify the timeout to 10 for it to run with local url
    def unit_test(self, depth=0):
    	seen = set()


        while len(self._url_queue):
	    	url, depth_ = self._url_queue.pop()

	        # skip this url; it's too deep
	        if depth_ > depth:
	        	continue

        	doc_id = self.document_id(url)
        	seen.add(doc_id) # mark this document as haven't been visited        
        	socket = None
        	try:
	    		socket = urllib2.urlopen(url, timeout=10)
	    		soup = BeautifulSoup(socket.read())
	    		self._curr_depth = depth_ + 1
	    		self._curr_url = url
	    		self._curr_doc_id = doc_id
	    		self._font_size = 0
	    		self._curr_words = [ ]
	    		self._index_document(soup)
	    		self._add_words_to_document()
	    		print "    url="+repr(self._curr_url)

	        except Exception as e:
	            print e
	            pass
	        finally:
	            if socket:
	                socket.close()


if __name__ == "__main__":
    
    bot = crawler(None, "lab4.txt")
    bot.crawl(depth=1)

    print "\n\n"
    print bot._lexicon
    print "\n\n"
    print bot._doc_index
    print "\n\n"
    print bot._inverted_index
    print "\n\n"
    
    res = bot.get_resolved_inverted_index()
    print res

    bot._conn.close()
