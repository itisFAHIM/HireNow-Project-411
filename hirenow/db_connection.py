from pymongo import MongoClient

def get_db():
    # Since you're installing MongoDB locally, we connect to localhost
    client = MongoClient("mongodb://localhost:27017/")
    # 'HireNowDB' is the name of your database in Mongo
    db = client['HireNowDB'] 
    return db   