#!/usr/bin/python
# -*- coding: utf-8 -*-
from re import I
from flask import Flask
from flask import request
import chromadb
from chromadb.config import Settings

app = Flask(__name__)

client = chromadb.Client(Settings(chroma_api_impl='rest',
                         chroma_server_host='localhost',
                         chroma_server_http_port=8000))


@app.route('/collections', methods=['GET', 'POST','DELETE'])
def create_or_get_collections():
    collection_name = request.args.get('name')
    collection = client.create_collection(collection_name,
            get_or_create=True)
    if request.method == 'DELETE':
        client.delete_collection(collection_name)
        return
    return dict(collection)


@app.route('/collections/<string:collection_name>', methods=['GET',
           'POST'])
def add_or_query_collection(collection_name):
    collection = client.create_collection(collection_name,
            get_or_create=True)

    if request.method == 'POST':
        request_data = request.get_json()
        collection_documents = request_data['documents']
        collection_ids = request_data['ids']
        collection.add(documents=collection_documents,
                       ids=collection_ids)
        return 'Documents successfully added to collection'
    else:
        query = request.args.get('query')
        result =  collection.query(query_texts=query, n_results=1)
        return result['documents'][0][0]

@app.route('/collections/<string:collection_name>/all', methods='GET')
def get_collection(collection_name):
    collection = client.create_collection(collection_name,
            get_or_create=True)
    total_count = collection.count()
    return dict(collection.peek(limit=total_count))


@app.route('/collections/<string:collection_name>', methods=['GET','DELETE'])
def delete_document(collection_name):
    collection = client.create_collection(collection_name,
            get_or_create=True)
    ids = request.args.get('ids')
    if request.method == 'GET':
        return dict(collection.get(ids=ids))
    else:
        collection.delete(ids=ids)

    

if __name__ == '__main__':
    app.run(host='192.168.144.129')
