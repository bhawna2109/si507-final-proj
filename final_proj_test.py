#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

import unittest
import json
import goodreads as goodreads

###### Part 1 ######
####################

class TestGoodreads(unittest.TestCase):
    def testgetbookshelves(self):
        g1 = goodreads.Goodreads()
        self.assertEqual(g1.get_all_bookshelves(), ["All", "Read", "Currently Reading", "Want to Read"])

unittest.main()
