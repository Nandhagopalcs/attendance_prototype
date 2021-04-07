import pymongo

client = pymongo.MongoClient("mongodb+srv://nandhu:hinandhu100@cluster0.q49fb.mongodb.net/attendance?retryWrites=true&w=majority")
db = client.test
db = client['attendance']
col = db['encoding']
post = {"_id": 1, "name":"JEFF", "attendence": 0}
col.insert_one(post)
print("complete")



