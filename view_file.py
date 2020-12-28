#imports
from flask import Flask, render_template, request
import os
import pickle
from model import SearchEngine 
import threading 
import string
from ctypes import windll
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fileresults.db'
db = SQLAlchemy(app)

# global varaibles
global single_directory 
single_directory = ""
global drives
drives = []
global search_term
search_term = ""

# Model class for storing and retriving data from database
class Model(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    searchTerm = db.Column(db.String(200),nullable=False)
    pathSearched = db.Column(db.String(200),nullable=False)
    result = db.Column(db.String(200),nullable=False)

    def __repr__(self):
        return '<FileEngine %r>' % self.id

# creating instance of SearchEngine Class
s = SearchEngine()


lock = threading.Lock()
thread = threading.Thread()

@app.route('/', methods=['POST','GET'])
def index():    
    return render_template("home.html")

""" function which handles essential operation of application,
it first checks whether the data to be searched from database or 
from loaded local drive, then it performs the respective opreations as required
 """
@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST': 
        global single_directory
        global drives
        global thread
        drives = str(drives)
        print(single_directory)
        print(drives)
        if single_directory == "" and drives == "[]":
            object_result ={
                "results" : 1,
                "status" : False,
                "message" : "Please ensure you have loaded any of the drive.",
                "success_message" : "",
                }
            return render_template("search.html",result=object_result)
        searchDB = request.form.get('searchDB')
        search_term = request.form['search_term']
        if searchDB == "on":
            if drives:
                result_from_db = []
                results = db.session.query(Model).filter(Model.searchTerm == search_term,Model.pathSearched==drives).all()
                if len(results) == 0:
                    result_from_db.append("No match found! Please uncheck search from database, to search in local system.")
                for r in results:
                    result_from_db.append(r.result)
                object_result ={
                    "search_term": search_term,
                    "results":result_from_db,
                    "success_message":"Results are obtained from database! Total "+ str(len(results))+" results are found.",
                    "directory":drives
                }
                return render_template("search.html",result=object_result)
            
            elif single_directory != "":
                result_from_db = []
                results = db.session.query(Model).filter(Model.searchTerm == search_term,Model.pathSearched==single_directory).all()
                if len(results) == 0:
                    result_from_db.append("No match found! Please uncheck search from database, to search in local system.")
                for r in results:
                    result_from_db.append(r.result)
                object_result ={
                    "search_term": search_term,
                    "results":result_from_db,
                    "success_message":"Results are obtained from database! Total "+ str(len(results))+" results are found.",
                    "directory":single_directory,
                }
                return render_template("search.html",result=object_result)
        else:
            object_result = s.search(search_term)
            object_result["search_term"] = search_term
            if drives != "":
                object_result["directory"] = drives
                if object_result.get('results') == 0:
                    pass
                else:
                    thread = threading.Thread(target=add_to_db, args=(object_result.get('results'),search_term,drives), daemon=True).start() 
            if single_directory != "":
                object_result["directory"] = single_directory
                if object_result.get('results') == 0:
                    pass
                else:
                    thread = threading.Thread(target=add_to_db, args=(object_result.get('results'),search_term,single_directory), daemon=True).start() 
            return render_template("search.html",result=object_result)
    return render_template("search.html",result={"results":1})

# this function is used to load single drive and then to create an index of it.
@app.route('/load_single', methods=['POST','GET'])
def single_load():
    if request.method == 'POST': 
        global single_directory
        global drives
        drives = ""
        single_directory = request.form['file_path']
        global thread 
        with lock:
            thread = threading.Thread(target=s.create_new_index, args=(single_directory,), daemon=True).start()
        return render_template("search.html",result={"results":1,"directory":single_directory})    
    return render_template("search.html",result={"results":1,"directory":single_directory})    

# it is used to load data onto file_index from file_index.pkl, should use this function if all drives are loded before. 
@app.route('/preloaded', methods=['POST','GET'])
def pre_load():
    if request.method == 'POST':
        global drives
        global single_directory
        single_directory = ""
        drives = no_of_drives() 
        s.load_existing_index()
        return render_template("search.html",result={"results":1,"directory":drives})    
    return render_template("search.html",result={"results":1,"directory":drives})    


# it finds out all the local drive in system, and then create index for all the directories.
@app.route('/multiple_load', methods=['POST','GET'])
def multiple_load():   
    if request.method == 'POST': 
        global drives
        global single_directory
        single_directory = ""
        s.file_index.clear()
        drives = no_of_drives()
        for a in drives:
            with lock:
                thread = threading.Thread(target=s.create_multiple_index, args=(a+':/',), daemon=True).start()
        return render_template("search.html",result={"results":1,"directory":drives})
    return render_template("search.html",result={"results":1,"directory":drives})        

# Add the result data to database
def add_to_db(results,search_term,single_directory):
    for a in results:
        newData = Model(searchTerm=search_term,pathSearched=single_directory,result=a)
        try:
            db.session.add(newData)
            db.session.commit()
        except:
            print("unable to add")
    print("All data are added")


# returns the number of local disk present in the system
def no_of_drives():
    drive = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive.append(letter)
        bitmask >>= 1
    return drive


# main function
if __name__ == "__main__":
    app.run(debug=False)
