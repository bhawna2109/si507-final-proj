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
from bs4 import BeautifulSoup

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

    def make_request(self, url, params = {}):
        key = self.construct_unique_key(url, params)
        if key in self.cache_dict:
            print("Cache Hit")
            return self.cache_dict[key].encode()
        else:
            print("Cache Miss. Please wait while your records are being fetched...")
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


class GoodreadsReview:
    def __init__(self, reviewid, reviewurl, rating, spoilerflag, snippet):
        self.reviewid = reviewid
        self.url = reviewurl
        self.rating = rating
        self.spoilerflag = spoilerflag
        self.snippet = snippet

    def infostring(self):
        return f'''Rated:{self.rating}/5.0, Has Spoiler: {self.spoilerflag}
{self.snippet} (Read full review at {self.url})
'''

class Book:
    def __init__(self, name = "", authors = [], description = "", rating = 0, goodReadsID = 0, goodReadsURL = "", reviews = [], previewURL = ''):
        self.name = name
        self.authors = authors
        self.description = description
        self.rating = rating
        self.goodReadsID = goodReadsID
        self.goodReadsURL = goodReadsURL
        self.reviews = reviews
        self.previewURL = previewURL

    def __str__(self):
        return f"{self.name} by {','.join(self.authors)}"

    def infostring(self):
        return f'''{self.name} by {','.join(self.authors)}
Average rating: {self.rating}/5
GoodReads: (ID:{self.goodReadsID}) {self.goodReadsURL}
{self.description}
Preview at {self.previewURL}
        '''
    
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
        params = {'v' : 2, 'key': self.key, 'id' : self.userid, 'shelf' : shelf_name}
        r = self.cache.make_request(url, params)
        books = []
        root = ET.fromstring(r)
        for book in root.iter("book"):
            title = book.find("title").text
            goodreadsid = book.find("id").text
            goodreadsurl = book.find("link").text
            rating = book.find("average_rating").text
            description = BeautifulSoup(book.find("description").text, 'html.parser').get_text().strip()
            authors = []
            for author in book.iter("author"):
                authors.append(author.find("name").text)
            reviews = self.get_reviews_for_book(goodreadsurl)
            previewurl = self.get_preview_url_for_book(title)
            books.append(Book(title, authors, description, rating, goodreadsid, goodreadsurl, reviews, previewurl))
        return books

    def get_preview_url_for_book(self, booktitle):
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {'q': booktitle}
        volumeid = json.loads(self.cache.make_request(url, params))["items"][0]["id"]
        newurl = f"https://www.googleapis.com/books/v1/volumes/{volumeid}"
        readerLink = json.loads(self.cache.make_request(newurl))["accessInfo"]["webReaderLink"]
        return(readerLink)

    def get_reviews_for_book(self, bookurl):
        response = self.cache.make_request(bookurl)
        soup = BeautifulSoup(response, 'html.parser')
        reviews = []
        for review in soup.find_all('div', itemprop="reviews"):
            reviewid = review.get('id').replace('review_', '')
            reviews.append(self.get_review_data_from_id(reviewid))
        return reviews

    def get_review_data_from_id(self, reviewid):
        url = 'https://www.goodreads.com/review/show.xml'
        params = {'key': self.key, 'id' : reviewid}
        r = self.cache.make_request(url, params)
        root = ET.fromstring(r)
        for review in root.iter("review"):
            reviewurl = 'https://www.goodreads.com/review/show/' + reviewid
            rating = review.find("rating").text
            spoilerflag = review.find("spoiler_flag").text
            snippet = BeautifulSoup(review.find("body").text, 'html.parser').get_text().strip()
        return GoodreadsReview(reviewid, reviewurl, rating, spoilerflag, snippet)

class BookDatabase:
    def __init__(self, db_name = "si507-final-proj"):
        self.db_name = db_name + '.sqlite'

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
    
        drop_books_sql = 'DROP TABLE IF EXISTS "Books"'
        create_books_sql = '''
            CREATE TABLE IF NOT EXISTS "Books" (
                "BookName"	    TEXT NOT NULL,
                "Author"	    TEXT NOT NULL,
                "BookDescription"   TEXT NOT NULL,
                "Rating"	    NUMERIC NOT NULL,
                "NumberOfReviews"   INTEGER NOT NULL,
                "GoodreadsID"	    NUMERIC NOT NULL PRIMARY KEY,
                "GoodreadsURL"	    TEXT NOT NULL,
                "BookPreviewURL"    TEXT NOT NULL
            )
        '''
        drop_reviews_sql = 'DROP TABLE IF EXISTS "Reviews"'
        create_reviews_sql = '''
            CREATE TABLE IF NOT EXISTS "Reviews" (
                "ReviewId"	    NUMERIC NOT NULL PRIMARY KEY,
                "GoodreadsID"   NUMERIC NOT NULL,
                "Review Rating"	    TEXT NOT NULL,
                "Has Spoilers"      TEXT NOT NULL,
                "Review Snippet"    TEXT NOT NULL,
                "Review URL"        TEXT NOT NULL
            )
        '''
        cur.execute(drop_books_sql)
        cur.execute(create_books_sql)
        cur.execute(drop_reviews_sql)
        cur.execute(create_reviews_sql)
        conn.commit()
        conn.close()
    
    def write_books_to_db(self, all_books):
        conn = sqlite3.connect(self.db_name)
        insert_books_sql = '''
            INSERT INTO Books
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        insert_reviews_sql = '''
            INSERT INTO Reviews
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cur = conn.cursor()
        for counter in range(len(all_books)):
            book = all_books[counter]
            cur.execute(insert_books_sql,
                [
                    book.name, ",".join(book.authors), book.description, book.rating, len(book.reviews), book.goodReadsID, book.goodReadsURL, book.previewURL
                ]
            )
            for review in book.reviews:
                cur.execute(insert_reviews_sql,
                    [
                        review.reviewid, book.goodReadsID, review.rating, review.spoilerflag, review.snippet, review.url
                    ]
                )

        conn.commit()
        conn.close()

    def execute_query(self, query):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        result = cursor.execute(query).fetchall()
        connection.close()
        print(result)

    def sql_analysis(self):
        print(f"You can enter some queries here and see what result you get:")
        resp = "junk"
        while(resp != "exit"):
            resp = input("Enter an SQL query or \"exit\" to quit: ")
            if resp == "exit":
                return
            self.execute_query(resp)




if __name__ == "__main__":
    print(f'''
    Hello there!
    Welcome to Bhawna Agarwal's SI507 final project.

    This is a tool that'll help you finalize the next book that you should read (based on your goodreads profile and guide you with your options in acquiring that book).

    You can use the interface below to do 2 things. You can either populate your database from the books you have in your goodreads profile. Or you can look up the existing database for help.
    
    To proceed, we will need you to do the following:
    1. Create a secrets.py so that you can access goodreads API. This should look like:
        GOODREADS_API_KEY = 'deadbeef'
        GOODREADS_API_SECRET = 'deadbeef'
    2. Keep a user-id handy that you'll be asked to input below. This is the number that shows up in the URL when you go to the My Books tab in your goodreads profile.

    ''')

    db = BookDatabase()
    resp = "junk"
    while(resp != "exit"):
        print("Enter your goodreads user-id to populate data in the database, or \"sql\" to access the exiting database (only valid) or \"exit\" to quit. Keep in mind that entering a goodreads id clears out the current database.")
        resp = input("Make your selection: ")
        if resp == "exit":
            exit()
        if resp == "sql":
            db.sql_analysis()
        if resp.isnumeric():
            break
    g = Goodreads(resp)
    db.init_db()
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
        db.write_books_to_db(books)
        print(f"These are all your books in the shelf \"{resp}\" The data from these books has been added to SQL database:")
        for num in range(len(books)):
            print(f"{num+1}: {books[num]}")
        resp = input("Enter the number of the book you'd like to know more about, or exit to exit: ")
        while(not(resp.isnumeric() and 1<=int(resp)<=len(books))):
            if resp == "exit":
                exit()
            resp = input("Invalid input :( Please enter the number of the book you'd like to know more about, or exit to exit: ")
        book_selected = books[int(resp)-1]
        print(f"{book_selected.infostring()}")
        for review in book_selected.reviews:
            print(f"{review.infostring()}")
