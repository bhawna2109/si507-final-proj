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
from flask import Flask, render_template, request

class RequestsCache:
    # Class for maintaining a cache.
    # This class intends for the the "user" of the cache
    # to only use the make_request function.
    # Rest everything is taken by the class itself
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
    # An object of type GoodreadsReview is used to pass along
    # all the relevant information regarding a particular review
    # like the review id on goodreads, the review's rating,
    # Whether the review contains spoilers or not
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
    # An object of type Book holds all the relevant information regarding
    # a particular book.
    # It knows the title, the authors, description, average rating etc.
    # and has list of reviews to go with it as well
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
    # The main class of this project.
    # This makes all the API calls to the goodreads as well as
    # scrapes the book page to get review ids etc.
    # This object instantiates a cache within it for all the
    # requests call for speed up.
    def __init__(self, userid = ''):
        self.key = secrets.GOODREADS_API_KEY
        self.secret = secrets.GOODREADS_API_SECRET
        self.userid = userid
        self.auth = OAuth1(self.key, self.secret)
        self.cache = RequestsCache()

    def setuserid(self, userid = ''):
        #Set a goodreads userid for this object.
        #That userid will then be used to look up all the information
        self.userid = userid

    def get_all_bookshelves(self):
        #Returns a list of all the bookshelves of the current user-id
        #Returns the names of all shelves on GoodReads
        url = "https://www.goodreads.com/shelf/list.xml"
        params = {'key': self.key, 'user_id' : self.userid}
        r = self.cache.make_request(url, params)
        root = ET.fromstring(r)
        shelves = []
        for shelf in root.iter("user_shelf"):
            shelves.append(shelf.find("name").text)
        return shelves

    def get_all_books_in_shelf(self, shelf_name):
        # Returns a list of all books (of type Book) that
        # are present in the user's specified shelf.
        # This function makes a call to the goodreads API to get all books.
        # It then populates a list with books recieved.
        # In addition it calls other functions of this object which get some reviews 
        # of the book and gets a preview url from google API
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
        # For a given book title, this function looks up google apis
        # and returns a url for previewing the book.
        # This helps someone get a feel of the book on whether they want
        # to get it or not.
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {'q': booktitle}
        volumeid = json.loads(self.cache.make_request(url, params))["items"][0]["id"]
        newurl = f"https://www.googleapis.com/books/v1/volumes/{volumeid}"
        readerLink = json.loads(self.cache.make_request(newurl))["accessInfo"]["webReaderLink"]
        return(readerLink)

    def get_reviews_for_book(self, bookurl):
        #For a given goodreads book url. This function scrapes the webpage
        #to get all the review ids on that page. This was required because the 
        #goodreads api does not natively support returning all the reviews
        #associated with a book.
        #After scraping, another function is called to get the relevant information
        #from that review. This function returns a list of object GoodreadsReview
        response = self.cache.make_request(bookurl)
        soup = BeautifulSoup(response, 'html.parser')
        reviews = []
        for review in soup.find_all('div', itemprop="reviews"):
            reviewid = review.get('id').replace('review_', '')
            reviews.append(self.get_review_data_from_id(reviewid))
        return reviews

    def get_review_data_from_id(self, reviewid):
        #This function looks up the goodreds API for the specified review id
        #and populates information like the review rating, spoiler flag, full 
        #review url and snippet of the first ~300 characters of the review.
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
    #Maintains all the database handling for this project.
    #Creates the database and the tables "Books" and "Reviews"
    #and populates that from the information collected from the GoodReads objects
    #This class also supports running SQL queries on the database for presentation purposes
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
        return result

    def table_query(self):
        query = '''
        SELECT Books.BookName, Author, Rating, SUM("Review Rating" LIKE "5") AS FIveStar, SUM("Review Rating" LIKE "4") AS FourStar, SUM("Review Rating" LIKE "3") AS ThreeStar, SUM("Review Rating" LIKE "2") AS TwoStar, SUM("Review Rating" LIKE "1") AS OneStar, Books.BookPreviewURL, Books.GoodreadsID
        FROM Reviews
            JOIN Books
                ON Books.GoodreadsID = Reviews.GoodreadsID
        GROUP BY Books.BookName
        '''
        return self.execute_query(query)

    def reviews_query(self, book, rating):
        query = f'''
        SELECT Reviews."Review Snippet", Reviews."Has Spoilers", Reviews."Review URL"
        FROM Reviews
	    JOIN Books
		    ON Books.GoodreadsID = Reviews.GoodreadsID
        WHERE Reviews."Review Rating" = "{rating}" AND Books.BookName = "{book}"
        '''
        return self.execute_query(query)


app = Flask(__name__)

g = Goodreads()
db = BookDatabase()

@app.route('/')
def index():
    return render_template('index.html') # just the static HTML

@app.route('/handle_form', methods=['POST'])
def handle_form():

    GoodreadsID = request.form["GoodreadsID"]
    g.setuserid(GoodreadsID)
    db.init_db()
    shelves = g.get_all_bookshelves()

    return render_template('bookshelf_choose.html', 
        shelves_list=shelves
    )

@app.route('/handle_form_shelves', methods=['POST'])
def handle_form_shelves():
    resp = request.form["shelves"]
    books = g.get_all_books_in_shelf(resp)
    db.write_books_to_db(books)
    return render_template('show_books.html',
        shelf = resp, results = db.table_query()
    )

@app.route('/show_reviews', methods=['POST'])
def show_reviews():
    book = request.form["book"]
    rating = request.form["rating"]
    return render_template('show_reviews.html',
        book = book, rating = rating, reviews = db.reviews_query(book, rating)
    )


if __name__ == "__main__":
    print('starting Flask app', app.name)  
    app.run(debug=True)
