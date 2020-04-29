#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

import unittest
import json
import finalproj

class TestGoodreads(unittest.TestCase):
    def testgetbookshelves(self):
        g1 = finalproj.Goodreads('20227451')
        self.assertEqual(g1.get_all_bookshelves(), ["read", "currently-reading", "to-read"])
    
    def testgetbookfromshelf(self):
        #Test to make sure each element is of class Book
        g1 = finalproj.Goodreads('20227451')
        for book in g1.get_all_books_in_shelf("to-read"):
            self.assertIsInstance(book, finalproj.Book)
    
    def testgetbookfromshelf(self):
        #Test to make sure each element is of class Book
        g1 = finalproj.Goodreads('20227451')
        for book in g1.get_all_books_in_shelf("to-read"):
            self.assertIsInstance(book, finalproj.Book)
    
    def testgetreview(self):
        #Test to make sure each element is of class Book
        g1 = finalproj.Goodreads('20227451')
        for book in g1.get_all_books_in_shelf("to-read"):
            reviews = g1.get_reviews_for_book(book.goodReadsURL)
            self.assertIsInstance(reviews, list)
            self.assertIsInstance(reviews[0], finalproj.GoodreadsReview)

    def testgetpreviewURL(self):
        #Test to make sure each element is of class Book
        g1 = finalproj.Goodreads('20227451')
        self.assertEqual(g1.get_preview_url_for_book("Homegoing"), "http://play.google.com/books/reader?id=fh-eCgAAQBAJ&hl=&printsec=frontcover&source=gbs_api")

class TestBook(unittest.TestCase):
    def teststr1(self):
        b1 = finalproj.Book("Sapiens", ["Yuval Noah Harari"])
        self.assertEqual(f"{b1}" , "Sapiens by Yuval Noah Harari")
        
unittest.main()
