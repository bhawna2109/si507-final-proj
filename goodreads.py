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
    def __init__(self):
        client_key = secrets.GOODREADS_API_KEY
        client_secret = secrets.GOODREADS_API_SECRET
        self.auth = OAuth1(client_key, client_secret)

    def get_all_bookshelves(self):
        #Returns a list of all the bookshelves of the current user
        pass

    def get_all_books_in_shelf(self, shelf_name):
        #Returns a list of object Book
        pass

    def get_googlebooks_link_of_book(self, book):
        #Access the google API and get the url link and other info
        pass
