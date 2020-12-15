import os
import pickle
from typing import Dict
from threading import Thread

class SearchEngine:
    ''' Create a search engine object '''

    def __init__(self):
        self.file_index = [] # directory listing returned by os.walk()
        self.results = [] # search results returned from search method
        self.matches = 0 # count of records matched
        self.records = 0 # count of records searched
        self.index_loaded = False
        self.no_of_directories = 0
        self.completed_directories = 0
        self.preload_completed = True


    def create_new_index(self, values) -> None:
        ''' Create a new file index of the root; then save to self.file_index. '''
        try:
            if values != "":
                self.file_index.clear()
                self.index_loaded = False
                self.file_index: list = [(root, files) for root, dirs, files in os.walk(values) if files] 
                self.index_loaded = True
                print(values+" created")
                return values + " created"
            else:
                return "provide valid directory"
        except:
            return "unable to create an index"
        

    def create_directory_index(self, values) -> None:
        ''' Create a new file index of the root; then save to self.file_index and to pickle file '''
        self.index_loaded = False
        a: list = [(root, files) for root, dirs, files in os.walk(values) if files]
        if a == []:
            path = values[0:3]
            term = values[3:]
            a = [(path,[term])]
        for var in a:
            self.file_index.append(var)
        
        # save index to file
        with open('file_index.pkl','wb') as f:
            pickle.dump(self.file_index, f)
        self.completed_directories += 1
        self.index_loaded = True

    def create_multiple_index(self, values) -> None:
        var = []
        obj = os.scandir(path=values)
        for entry in obj:
            if entry.is_dir() or entry.is_file():
                var.append(str(entry.path))
        self.no_of_directories += len(var)
        for v in var:
            Thread(target=self.create_directory_index, args=(v,), daemon=True).start()
  
    def load_existing_index(self) -> None:
        ''' Load an existing file index into the program '''
        self.file_index.clear()
        self.index_loaded = False
        try:
            with open('file_index.pkl','rb') as f:
                self.file_index = pickle.load(f)
                self.index_loaded = True
        except:
            self.preload_completed = False
        


    def search(self, value) -> None:
        ''' Search for the term based on the type in the index;  '''
        self.results.clear()
        self.matches = 0
        self.records = 0
        term = value
        completed = False

        # if preloaded before loading drives atleast once
        if self.preload_completed == False:
            to_return = {
                "results" : 1,
                "status" : False,
                "message" : "Please ensure you loaded all the drives atleat once! before using 'Already Loaded' option, Seems like you are not loaded the drives before.",
                "success_message" : "",
                }
            return to_return

        # if not yet loaded
        if self.index_loaded == False:
            to_return = {
                "results" : 0,
                "status" : True,
                "message" : "",
                "success_message" : "",
                }
            return to_return

        
        # search for matches and count results
        for path, files in self.file_index:
            for file in files:
                self.records +=1
                if ( term.lower() in file.lower() ):
                    result = path.replace('\\','/') + '/' + file
                    self.results.append(result)
                    self.matches +=1
                else:
                    continue 
        
        # save results to file
        # with open('search_results.txt','w') as f:
        #     for row in self.results:
        #         f.write(row + '\n')

        # if all the directories are loaded
        if self.no_of_directories == self.completed_directories:
            completed = True

        # if no match found
        if len(self.results) == 0:
            self.results.append("No match found!")
        
        # messages for user
        success_message = "Searched " + str(self.records) + " records and found " + str(self.matches) + " matches"
        message = "Not all directories are loaded, some are loading in different threads, and will be completed soon. " + str(self.completed_directories) + " out of " + str(self.no_of_directories) + " directories."
        
        # dict to be return back
        to_return = {
            "results" : self.results,
            "status" : completed,
            "message" : message,
            "success_message" : success_message,
        }
        return to_return
