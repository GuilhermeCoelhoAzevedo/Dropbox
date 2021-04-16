from application import app, client
from application.storage import blobList, addDirectory, addFile, delete_blob, downloadBlob

from flask import Flask, render_template, request, session, url_for, redirect, flash, json, jsonify, Response

from google.cloud import datastore
import google.oauth2.id_token
from google.auth.transport import requests

from operator import itemgetter
import re
import hashlib

firebase_request_adapter = requests.Request()

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
@app.route("/home/<id>", methods=['GET', 'POST'])
def home(id=""):
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    if not id:
        id = session['home']

    directory = client.get(client.key('Directory', int(id)))

    if not directory:
        return render_template('login.html', login=True)

    fileData        = []
    directoryData   = []
    navBar          = []
    user            = client.key('User', int(session['id']))

    query       = client.query(kind='Directory')
    query.add_filter("User", "=", user)
    pathData    = list(query.fetch())

    query       = client.query(kind='File')
    query.add_filter("User", "=", user)
    files       = list(query.fetch())

    blob_list   = blobList(directory["path"], "/")

    #GETTING FILES
    for i in blob_list:
        if i.name == directory["path"]:
            continue

        for element in files:
            if element['path'] == i.name:
                config = {
                    "name": i.name[len(directory["path"]):],
                    "id": element.key.id,
                    "path": element['path']
                }

                fileData.append(config)

    #GETTING FOLDERS
    for prefix in blob_list.prefixes:
        for element in pathData:
            if element['path'] == prefix:
                config = {
                    "name": prefix[len(directory["path"]):-1],
                    "id": element.key.id,
                    "path": prefix
                }

                directoryData.append(config)
 
    directoryData.sort(key=itemgetter('name'))
    fileData.sort(key=itemgetter('name'))
    
    startc          = 0
    count           = 0
    path            = ""
    navList         = list(re.finditer('/', directory['path']))
    
    #CREATING NAVEGATION MENU
    for x in navList:
        path  += directory['path'][startc:x.end()]
        folder = directory['path'][startc:x.start()]
        startc = x.start() + 1
        count += 1
        active = 0

        if count == 1:
            folder = "Home"

        if count == len(navList):
            active = 1
    
        for element in pathData:
            if element['path'] == path:
                navBar.append({"folder" : folder, "id" : element.key.id, "active" : active})
                break

    return render_template("home.html", directoryData=directoryData, fileData=fileData, parentDirectory=directory, navBar=navBar)

@app.route("/login", methods=['GET', 'POST'])
def login():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    session.pop('id', None)
    session.pop('email', None)
    session.pop('home', None)

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            
            #CONTROL USER SESSION
            session['email']    = claims['email']

            query = client.query(kind='User')
            query.add_filter("email", "=", session['email'])
            userData = list(query.fetch())

            if not userData:
                user = datastore.Entity(key = client.key('User'))
        
                user.update({
                    'email' : session['email']
                })

                client.put(user)
                session['id'] = user.key.id

                direc = datastore.Entity(key = client.key('Directory'))

                direc.update({
                    'path' : session['email'] + "/",
                    'User' : user.key
                })

                client.put(direc)

                addDirectory(session['email'] + "/")
            else:
                for user in userData:
                    session['id'] = user.key.id
                    path = user['email'] + '/'

                query = client.query(kind='Directory')
                query.add_filter("path", "=", path)
                dirData = list(query.fetch())

                for element in dirData:
                    direc = element

            session['home'] = direc.key.id
            flash(f"{claims['email']}, you are successfully logged in!", "success")

            return redirect(url_for("home"))

        except ValueError as exc:
            error_message = str(exc)
            flash("Sorry, something went wrong!", "danger")

    return render_template('login.html', login=True)

@app.route("/logout")
def logout():
    session.pop('id', None)
    session.pop('email', None)
    session.pop('home', None)

    return redirect(url_for('login'))

@app.route("/createFolder", methods=['POST'])
def createFolder():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    #AJAX FOR CREATE FOLDER
    if request.method == 'POST':
        if request.is_json:         
            parameters      = request.get_json(force=True)
            status          = []

            if not parameters['folder']:
                return False

            if parameters['id']:
                idParent = parameters['id']
            else:
                idParent = session['home']

            parent_dir  = client.get(client.key('Directory', int(idParent)))
            direc       = datastore.Entity(key = client.key('Directory'))
            user        = client.key('User', int(session['id']))
            folder      = parameters['folder'].strip()

            query = client.query(kind='Directory')
            query.add_filter("User", "=", user)
            query.add_filter("path", "=", parent_dir['path'] + folder)
            pathData = list(query.fetch())

            if not pathData:
                direc.update({
                    'path' : parent_dir['path'] + folder,
                    'User' : user
                })

                client.put(direc)

                addDirectory(parent_dir['path'] + folder)

                status.append([0, direc.key.id])
            else:
                flash(f"{folder[:-1]} folder already exist in the current folder!", "danger")
                status.append([1, "Folder already exist!"])

            results = json.dumps(status)

            return results

@app.route("/deleteFolder", methods=['POST'])
def deleteFolder():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    user = client.key('User', int(session['id']))

    #CHECKING IF THERE IS STILL FOLDERS INSIDE
    query = client.query(kind='Directory')
    query.add_filter("User", "=", user)
    dirData = query.fetch()
    folderName = request.form['path'][len(request.form['pathParent']):-1]

    for element in dirData:
        if element['path'] == request.form['path']:
            continue

        if request.form['path'] in element['path']:
            flash(f"{folderName} still has folders inside!", "danger")
            
            return redirect(url_for("home", id=request.form['idParent']))

    #CHECKING IF THERE IS STILL FILES INSIDE
    query = client.query(kind='File')
    query.add_filter("User", "=", user)
    fileData = query.fetch()

    for element in fileData:
        if request.form['path'] in element['path']:
            flash(f"{folderName} still has files inside!", "danger")
            
            return redirect(url_for("home", id=request.form['idParent']))

    #DELETING FOLDER
    delete_blob(request.form['path'])

    entity_key  = client.key("Directory", int(request.form['idFolder']))
    client.delete(entity_key)

    return redirect(url_for("home", id=request.form['idParent']))

@app.route('/uploadFile', methods=['POST'])
def uploadFile():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    file = request.files['file_name']
    
    fileEntity  = datastore.Entity(key = client.key('File'))
    user        = client.key('User', int(session['id']))

    fileEntity.update({
        'path' : request.form['path'] + file.filename,
        'User' : user,
        'users_shared' : []
    })

    client.put(fileEntity)

    addFile(request.form['path'], file)

    return redirect(url_for("home", id=request.form['idParent']))

@app.route("/deleteFile", methods=['POST'])
def deleteFile():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    delete_blob(request.form['path'])

    entity_key  = client.key("File", int(request.form['idFile']))
    client.delete(entity_key)

    return redirect(url_for("home", id=request.form['idParent']))

@app.route("/downloadFile", methods=['POST'])
def downloadFile():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    name = request.form['filename']
    path = request.form['path']

    if not path:
        return False

    return Response(downloadBlob(path), mimetype='application/octet-stream', headers={"Content-Disposition": "filename=" + name})

@app.route("/findDuplicates", methods=['POST'])
def findDuplicates():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    #AJAX FOR DUPLICATED FILES
    if request.method == 'POST':
        if request.is_json:         
            parameters = request.get_json(force=True)

            if not parameters:
                return False

            if not parameters['idParent']:
                folder = session['home']
            else:
                folder = parameters['idParent']

            if parameters['lookAll']:
                directory = client.get(client.key('Directory', int(session['home'])))
                blob_list = blobList(directory["path"])
            else:
                directory = client.get(client.key('Directory', int(folder)))
                blob_list = blobList(directory["path"], "/")
            
            files_duplicated    = []
            return_list         = []
            hash_storage    	= {}
            
            #GETTING HASH FILES
            for i in blob_list:
                if i.name[-1] == "/":
                    continue
                
                if i.md5_hash not in hash_storage:
                    hash_storage[i.md5_hash]=[]
                
                hash_storage[i.md5_hash].append(i.name)

            #CHECKING DUPLICATES
            for key, r_files in hash_storage.items():
                if len(r_files) <= 1:
                    continue

                for path in r_files:
                    x       = list(re.finditer('/', path))[0]
                    name    = path[x.end():]

                    files_duplicated.append(name)

                return_list.append(files_duplicated)
                files_duplicated = []

            results = json.dumps(return_list)
            return results