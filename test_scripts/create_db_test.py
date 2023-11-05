import sys
sys.path.insert(0, '..')
import database

db = database.Database("test.db")
db.connect()
db.close()