#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import secrets # file that contains your OAuth credentials
import xml.etree.ElementTree as ET

class RequestsCache:
    def __init__(self, file_name = "cache.json"):
        self.file_name = file_name
        try:
            cache_file = open(file_name, 'r')
            cache_contents = cache_file.read()
            cache_file.close()
            self.cache_dict = json.loads(cache_contents)
        except:
            self.cache_dict = {}

    def make_request(self, url, params):
        key = self.construct_unique_key(url, params)
        if key in self.cache_dict:
            print("Cache Hit")
            return self.cache_dict[key].encode()
        else:
            r = requests.get(url = url, params = params)
            self.cache_dict[key] = r.content.decode()
            self.save_cache()
            return self.cache_dict[key].encode()
    
    def save_cache(self):
        dumped_json_cache = json.dumps(self.cache_dict)
        fw = open(self.file_name,"w")
        fw.write(dumped_json_cache)
        fw.close()      

    def construct_unique_key(self, baseurl, params):
        param_strings = []
        connector = '_'
        for k in params.keys():
            param_strings.append(f'{k}_{params[k]}')
        param_strings.sort()
        unique_key = baseurl + connector +  connector.join(param_strings)
        return unique_key


class GoogleBooks:
    def __init__(self, url = ""):
        self.url = url

class Book:
    def __init__(self, name = "", author = []):
        self.name = name
        self.author = author
        self.googlebooks = ""

    def __str__(self):
        return f"{self.name} by {','.join(self.author)}"
    
    def initialize_googlebooks_link(self):
        url = "" #FIXME
        #self.googlebooks = GoogleBooks(url)

class Goodreads:
    def __init__(self, userid = ''):
        self.key = secrets.GOODREADS_API_KEY
        self.secret = secrets.GOODREADS_API_SECRET
        self.userid = userid
        self.auth = OAuth1(self.key, self.secret)
        self.cache = RequestsCache()

    def get_all_bookshelves(self):
        #Returns a list of all the bookshelves of the current user
        url = "https://www.goodreads.com/shelf/list.xml"
        params = {'key': self.key, 'user_id' : self.userid}
        r = self.cache.make_request(url, params)
        root = ET.fromstring(r)
        shelves = []
        for shelf in root.iter("user_shelf"):
            shelves.append(shelf.find("name").text)
        return shelves

    def get_all_books_in_shelf(self, shelf_name):
        url = "https://www.goodreads.com/review/list?v=2"
        params = {'v' : 2, 'key': self.key, 'id' : self.userid, 'shelf' : shelf_name, 'sort' : "title, author, rating, review"}
        r = self.cache.make_request(url, params)
        books = []
        root = ET.fromstring(r)
        for book in root.iter("book"):
            title = book.find("title").text
            books.append(Book(title))
        for book in books:
            print(f"{book}")
        return books

