import unittest
from model import SearchEngine

class TestFileSearchEngine(unittest.TestCase):
    
    def setUp(self):
        self.s = SearchEngine()

    def test_create_new_index(self):
        self.assertEqual(self.s.create_new_index("D:/"),"D:/ created")

    def test_load_existing_index(self):
        self.s.load_existing_index()

        # if index is already lodaed the following self.s.index_loaded will be true
        self.assertTrue(self.s.index_loaded)

        # if index is not lodaed before the following self.s.preload_completed will be false
        # self.assertFalse(self.s.preload_completed)

    def test_search_from_existing_index(self):        
        # loading already created index from pickle file
        self.s.load_existing_index()
  
        # calling search function with file name
        search = self.s.search("pdfjfuhareugh")

        # if preloading fails the following self.s.preload_completed will be false
        # self.assertFalse(self.s.preload_completed)

        # if file found, the status will show as completed
        # self.assertTrue(search['status'])

        # if file not found, result will return message as "No match found!"
        self.assertListEqual(search['results'],["No match found!"])

    def test_search_from_new_index(self):
        index = self.s.create_new_index("D:/")
        
        # calling search function with file name
        search = self.s.search("pdf")

        # if loading of index fails the following self.s.preload_completed will be false
        self.assertEqual(index,"D:/ created")

        # if file found, the status will show as completed
        self.assertTrue(search['status'])

        # if file not found, result will return message as "No match found!"
        # self.assertListEqual(search['results'],["No match found!"])        
if __name__ == '__main__':
    unittest.main()