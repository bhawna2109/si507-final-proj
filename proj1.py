#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import secrets # file that contains your OAuth credentials
import xml.etree.ElementTree as ET

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

    def get_all_bookshelves(self):
        #Returns a list of all the bookshelves of the current user
        url = "https://www.goodreads.com/shelf/list.xml"
        params = {'key': self.key, 'user_id' : self.userid}
        r = requests.get(url = url, params = params)
        root = ET.fromstring(r.content)
        shelves = []
        for shelf in root.iter("user_shelf"):
            shelves.append(shelf.find("name").text)
        return shelves

    def get_all_books_in_shelf(self, shelf_name):
        #Returns a list of object Book
        pass

