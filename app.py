import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import face_recognition
import cv2
import os
from werkzeug.utils import secure_filename
import pymongo

client = pymongo.MongoClient("mongodb+srv://nandhu:hinandhu100@cluster0.q49fb.mongodb.net/attendance?retryWrites=true&w=majority")
db = client.test
db = client['attendance']
col = db['encoding']
coll=db['present']


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    ''' 
    image = request.files['imagefile']
    basepath = os.path.dirname(__file__)
    file_path = os.path.join(
            basepath, 'static', secure_filename(image.filename))
    
    image.save(file_path)
    print(file_path)
    #print(image)
    trial = face_recognition.load_image_file(file_path)
    trials = cv2.resize(trial,(0,0),None,0.25,0.25)
    img = cv2.cvtColor(trials,cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)
    
    req = request.form
    formdata = req.to_dict()
    f_name = req.get("name")
    f_id = req.get("id")
    #print(type(encode))
    #print(encode)
    #print(encode.pop())
    enc=list(encode.pop())
    #print(enc)
    post = {"_id": f_id, "name":f_name,"encode":enc,"image":image.filename}
    col.insert_one(post)
    print(image.filename)
    
    return render_template('added.html',val_name=f_name,val_id=f_id,st=1,usi=image.filename)

@app.route('/find',methods=['Post'])
def find():
    image=request.files['imgfile']
    basepath = os.path.dirname(__file__)
    file_path = os.path.join(
            basepath, 'static2', secure_filename(image.filename))
    
    image.save(file_path)
    print(file_path)
    trials = face_recognition.load_image_file(file_path)
    img = cv2.cvtColor(trials,cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(img)
    encodesCurFrame = face_recognition.face_encodings(img,facesCurFrame)
    #print(type(encodesCurFrame))
    
    results= col.find({})
    classNames=[]
    encodeListKnown=[]
    for result in results:
        classNames.append(result["name"])
        encodeListKnown.append(result['encode'])
    
    PresentNames=[]
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        if min(faceDis) < 0.55:
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                name = classNames[matchIndex]
                #print(name)
                PresentNames.append(name)
    
    setname = set(PresentNames)
    p_setname=list(setname)
    #print(setname)
    postp = {"name":p_setname}
    coll.insert_one(postp)

    extention=[]
    for x in p_setname:
        rs= col.find({"name":x})
        #extention.append(rs["ime"])
        for rt in rs:
            extention.append(rt['image'])
    
    print("complete")
    os.remove(file_path)
    return render_template('attended.html',val=p_setname,vall=extention)


if __name__ == "__main__":
    app.run(debug=True)