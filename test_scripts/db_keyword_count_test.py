import sys
sys.path.insert(0, '..')
import database

db = database.Database("test.db", None)
db.initialize_database()

test_dict = {'test1': 1,
             "test2": 3}

db.update_keywords(test_dict)
print(db.fetch_all_keyword_count())

test_dict2 = {'test1': 100,
             "test2": 300}

db.update_keywords(test_dict2)
print(db.fetch_all_keyword_count())