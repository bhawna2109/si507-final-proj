#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import secrets # file that contains your OAuth credentials
import xml.etree.ElementTree as ET

class Book:
    def __init__(self, name = "", author = ""):
        self.name = name
        self.author = author

    def __str__(self):
        return f"{self.name} by {self.author}"

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
        print(r.content)
        pass

    def get_all_books_in_shelf(self, shelf_name):
        #Returns a list of object Book
        pass

    def get_googlebooks_link_of_book(self, book):
        #Access the google API and get the url link and other info
        pass
