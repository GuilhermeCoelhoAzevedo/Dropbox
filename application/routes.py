from application import app, client

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

    return render_template("home.html")

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

