from application import app, client
from application.storage import blobList, addDirectory, delete_blob, downloadBlob

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

    directoryData   = []
    user            = client.key('User', int(session['id']))

    query       = client.query(kind='Directory')
    query.add_filter("User", "=", user)
    pathData    = list(query.fetch())

    blob_list   = blobList(directory["path"], "/")

    #GETTING FILES
    for i in blob_list:
        if i.name == directory["path"]:
            continue

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
    
    startc          = 0
    count           = 0
    path            = ""
    navList         = list(re.finditer('/', directory['path']))
    
    return render_template("home.html", directoryData=directoryData, parentDirectory=directory)

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

    #DELETING FOLDER
    delete_blob(request.form['path'])

    entity_key  = client.key("Directory", int(request.form['idFolder']))
    client.delete(entity_key)

    return redirect(url_for("home", id=request.form['idParent']))