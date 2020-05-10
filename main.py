#!/usr/bin/env python

# tools
import json
import uuid
import logging
from markupsafe import escape

from flask import Flask, request, render_template, jsonify, abort
from mongoengine import *

# app declaration
app = Flask(__name__)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# db connection
connect('groceries', host="mongodb")

### MODELS ###
class Item(EmbeddedDocument):
    id = StringField()
    text = StringField()
    checked = BooleanField(default=False)
    askedCount = IntField(default=1)
    boughtCount = IntField(default=1)

class Liste(Document):
    id = StringField(primary_key=True)
    items = ListField(EmbeddedDocumentField(Item))

### ROUTES ###
@app.route("/")
def main():
    random_id = uuid.uuid4()
    return render_template('index.html', random_id=str(random_id))

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("static/favicon.ico")

@app.route("/<string:listeKey>", methods=["GET", "POST"])
def show_groceries(listeKey):
    # retrieve list
    liste = Liste.objects(id=listeKey).first()
    if liste is None:
        liste = Liste(id=listeKey)

    if request.method == "POST":
        i = Item(id=str(uuid.uuid4()), text=request.form["new_value"])
        app.logger.debug("adding item %s to liste %s", i, liste)
        liste.items.append(i)

        app.logger.debug("Saving liste %s", liste.to_json())
        liste.save()
    
    if request.accept_mimetypes.accept_html:
        return render_template('liste.html', liste=liste)
    elif request.accept_mimetypes.accept_json:
        return jsonify(liste)
    else:
        abort(400)

@app.route("/<string:listeKey>/<string:itemKey>", methods=["POST", "DELETE"])
def toggleItem(listeKey, itemKey):
    liste = Liste.objects(id=listeKey).first()

    if liste is None:
        abort(404)

    # TODO: use mongo update
    if request.method == "POST":
        for item in liste.items:
            if item.id == itemKey:
                # TOGGLE
                item.checked ^= False
                break
    elif request.method == "DELETE":
        liste.items = [
                e for e in liste.items
                if e.id != itemKey
        ]
    liste.save()
    
    return '', 204
