from application import app, client, google
from application.storage import blobList, addDirectory, addFile, delete_blob, downloadBlob, getBlob

from flask import render_template, request, session, url_for, redirect, flash, json, Response

from google.cloud import datastore

from operator import itemgetter
import re

@app.route("/")
@app.route("/home")
@app.route("/home/<id>")
def home(id=""):
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    if not id:
        id = session['home']

    directory = client.get(client.key('Directory', int(id)))

    if not directory:
        return render_template('login.html', login=True)

    file_data       = []
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

                file_data.append(config)

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
    file_data.sort(key=itemgetter('name'))
    
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

    return render_template("home.html", directoryData=directoryData, file_data=file_data, parentDirectory=directory, navBar=navBar)

@app.route("/login", methods=['GET', 'POST'])
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri, prompt="select_account")

@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()

    # Pass the nonce stored in the session to verify the ID token
    user_info = google.parse_id_token(token, nonce=session.get('nonce'))

    # STORE USER SESSION
    session['email'] = user_info['email']

    # CHECK IF USER EXISTS
    query = client.query(kind='User')
    query.add_filter("email", "=", session['email'])
    userData = list(query.fetch())

    if not userData:
        # CREATE USER ENTITY
        user = datastore.Entity(key=client.key('User'))
        user.update({'email': session['email']})
        client.put(user)
        session['id'] = user.key.id

        # Create user root directory
        directory = datastore.Entity(key=client.key('Directory'))

        directory.update({
            'path': session['email'] + "/",
            'User': user.key
        })

        client.put(directory)

        addDirectory(session['email'] + "/")
    else:
        #Creates root path based on email
        user = userData[0]
        session['id'] = user.key.id
        path = user['email'] + '/'

        # Query directories with the email
        query = client.query(kind='Directory')
        query.add_filter(filter=("path", "=", path))
        directories = list(query.fetch())

        # Get user root directory
        directory = next((d for d in directories if d['path'] == path), "")

    session['home'] = directory.key.id
    flash(f"{session['email']}, you are successfully logged in!", "success")
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")

    # Redirect to Google's logout URL
    google_logout = "https://accounts.google.com/Logout"
    return redirect(google_logout)

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
    file_data = query.fetch()

    for element in file_data:
        if request.form['path'] in element['path']:
            flash(f"{folderName} still has files inside!", "danger")
            
            return redirect(url_for("home", id=request.form['idParent']))

    #DELETING FOLDER
    delete_blob(request.form['path'])

    entity_key  = client.key("Directory", int(request.form['idFolder']))
    client.delete(entity_key)

    return redirect(url_for("home", id=request.form['idParent']))

@app.route('/checkFile', methods=['POST'])
def check_file():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    #AJAX FOR CHECKING IF FILE EXIST
    if request.method == 'POST':
        if request.is_json:         
            parameters      = request.get_json(force=True)
            blob_exist      = []

            if not parameters['file']:
                return False

            if parameters['idPath']:
                idPath = parameters['idPath']
            else:
                idPath = session['home']

            x           = list(re.finditer('/', parameters['file']))[-1]
            file        = parameters['file'][x.end():]

            directory   = client.get(client.key('Directory', int(idPath)))
            path        = directory['path'] + file

            blob = getBlob(path)

            if blob:
                blob_exist.append([True, file])
            else:
                blob_exist.append([False, file])

            results = json.dumps(blob_exist)

            return results

@app.route('/uploadFile', methods=['POST'])
def uploadFile():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    file = request.files['file_name']
    
    fileEntity  = datastore.Entity(key = client.key('File'))
    user        = client.key('User', int(session['id']))

    query       = client.query(kind='File')
    query.add_filter("path", "=", request.form['path'] + file.filename)
    file_data    = list(query.fetch())

    if not file_data:
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

@app.route("/shareFile", methods=['POST'])
def shareFile():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    email       = request.form['email']
    id_return   = request.form['idParent']
    id_file     = request.form['idFile']

    if session['email'] == email:
        flash("You can't share a file with yourself!", "danger")
        return redirect(url_for("home", id=id_return))

    query = client.query(kind='User')
    query.add_filter("email", "=", email)
    userData = list(query.fetch())

    if userData:
        for element in userData:
            user = element
    else:
        flash("File not shared! Email doesn't exist in the system.", "danger")
        return redirect(url_for("home", id=id_return))


    file = client.get(client.key('File', int(id_file)))
    users_shared = file['users_shared']

    if user.key.id in users_shared:
        flash(f"File already shared with {email}", "danger")
        return redirect(url_for("home", id=id_return))        

    users_shared.append(user.key.id)

    file.update({
        'users_shared' : users_shared
    })

    client.put(file)
    
    flash(f"File shared with {email}", "success")

    return redirect(url_for("home", id=id_return))

@app.route("/sharedFiles")
def sharedFiles():
    #CHECK IF USER IS LOGGED IN
    if not session.get('email'):
        return redirect(url_for("login"))

    file_data    = []
    user        = client.get(client.key('User', int(session['id'])))

    query       = client.query(kind='File')
    files       = list(query.fetch())

    for element in files:
        if element['path'][-1:] == "/":
            continue

        if user.key.id in element['users_shared']:
            owner   = client.get(element['User'])
            x       = list(re.finditer('/', element['path']))[-1]
            name    = element['path'][x.end():]

            config = {
                "name": name,
                "id": element.key.id,
                "path": element['path'],
                "owner": owner['email']
            }

            file_data.append(config)            

    return render_template("sharedFiles.html", file_data=file_data, shared=True)