#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

import unittest
import json
import proj1

###### Part 1 ######
####################

class TestGoodreads(unittest.TestCase):
    def testgetbookshelves(self):
        g1 = proj1.Goodreads('20227451')
        self.assertEqual(g1.get_all_bookshelves(), ["read", "currently-reading", "to-read"])

class TestBook(unittest.TestCase):
    def teststr1(self):
        b1 = proj1.Book("Sapiens", ["Yuval Noah Harari"])
        self.assertEqual(f"{b1}" , "Sapiens by Yuval Noah Harari")
        

class TestGoogleBooks(unittest.TestCase):
    pass

unittest.main()
