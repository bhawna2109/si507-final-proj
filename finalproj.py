#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import secrets # file that contains your OAuth credentials
import xml.etree.ElementTree as ET
import sqlite3

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
        return books

def create_db():
    conn = sqlite3.connect('si507-final-proj.sqlite')
    cur = conn.cursor()

    drop_books_sql = 'DROP TABLE IF EXISTS "Books"'
    
    create_books_sql = '''
        CREATE TABLE IF NOT EXISTS "Books" (
            "Id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            "BookName"	TEXT NOT NULL,
            "Author"	TEXT NOT NULL,
            "BookDescription"	TEXT NOT NULL,
            "Rating"	NUMERIC NOT NULL,
            "NumberOfReviews"	INTEGER NOT NULL,
            "GoodreadsURL"	TEXT NOT NULL,
            "GoogleBooksId"	TEXT NOT NULL,
            "GoogleBooksURL"	TEXT NOT NULL
        )
    '''
    cur.execute(drop_books_sql)
    cur.execute(create_books_sql)
    conn.commit()
    conn.close()


def load_books(all_books):
    insert_books_sql = '''
        INSERT INTO Books
        VALUES (NULL, ?, "dsad", "sada", "4.5", "6", "sfs", "Sfs", "sff")
    '''
    conn = sqlite3.connect('si507-final-proj.sqlite')
    cur = conn.cursor()
    for num in range(len(all_books)):
        cur.execute(insert_books_sql,
            [
                all_books[num].name
            ]
        )
    conn.commit()
    conn.close()
    print ("i'm here")


if __name__ == "__main__":
    print(f'''
    Hello there!
    Welcome to Bhawna Agarwal's SI507 final project.

    This is a tool that'll help you finalize the next book that you should read (based on your goodreads profile and guide you with your options in acquiring that book).
    
    To proceed, we will need you to do the following:
    1. Create a secrets.py so that you can access goodreads API. This should look like:

        GOODREADS_API_KEY = 'deadbeef'
        GOODREADS_API_SECRET = 'deadbeef'
    
    2. Keep a user-id handy that you'll be asked to input below. This is the number that shows up in the URL when you go to the My Books tab in your goodreads profile.

    ''')

    resp = input("Enter your goodreads user-id or \"exit\" to quit: ")
    create_db()
    if resp == "exit":
        exit()
    g = Goodreads(resp)
    while(resp != "exit"):
        resp = "abcxyzjunk"
        shelves = g.get_all_bookshelves()
        print(f"These are all your bookshelves on your goodreads profile:")
        print("\n".join(shelves))
        resp = input("Enter the name of the shelf you'd like to go into, or exit to exit: ")
        while (resp not in shelves):
            if resp == "exit":
                exit()
            resp = input("Invalid input :( Please enter the name of the shelf you'd like to go into, or exit to exit: ")
        books = g.get_all_books_in_shelf(resp)
        load_books(books)
        print(f"These are all your books in the shelf \"{resp}\"  :")
        for num in range(len(books)):
            print(f"{num+1}: {books[num]}")
        resp = input("Enter the number of the book you'd like to know more about, or exit to exit: ")
        while(not(resp.isnumeric() and 1<=int(resp)<=len(books))):
            if resp == "exit":
                exit()
            resp = input("Invalid input :( Please enter the number of the book you'd like to know more about, or exit to exit: ")
        book_selected = books[int(resp)-1]
        print(f"You have selected book {book_selected}")