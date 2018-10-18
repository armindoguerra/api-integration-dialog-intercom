#!/usr/bin/env python

import json
import os
import re
from flask import Flask
from flask import request, jsonify
import requests
from pymongo import MongoClient
import datetime


# Flask app should start in global layout
app = Flask(__name__)


@app.route('/', methods=['POST'])
def control():
    
    # Recebe em formato JSON a notificação enviada pela Api Intercom
    req = request.get_json(silent=True, force=True)
    
    # Extraindo as informações necessárias para a conversa
    userid = req['data']['item']['user']['id']
    conversationid =  req['data']['item']['id']
    deliveryattempts = req['delivery_attempts']


    # Bloco condicional para identificar se é o início de uma nova conversa ou apenas uma resposta
    
    if req['topic'] == 'conversation.user.created':
    	usermessage = req['data']['item']['conversation_message']['body']
    	
    	# Invocando a função para limpas as tags html da mensagem
    	usermessage = cleanHtmlTags(usermessage)

    	# Enviando mensagem digitada pelo usuário para o bot (Dialogflow) responder 
    	response = getResponseFromDialogflow(usermessage, conversationid)
    	
    	# Construindo a responsta para o usuário e enviado para API Intercom mostrar no chat
    	print("userid: %s, conversationid: %s, usermessage: %s, response: %s" %(userid,conversationid,usermessage,response))
    	replyToUser(response,conversationid,userid)

    	# Estruturando os dados para armazeznar no MongoDB
    	conv = {
    		"userIntercomId":userid,
    		"conversationIntercomId":conversationid,
    		"userMessage":usermessage,
    		"responseBot":response,
    		"data": datetime.datetime.utcnow()
    	}

    else:
    	usermessage = req['data']['item']['conversation_parts']['conversation_parts'][0]['body']
    	usermessage = cleanHtmlTags(usermessage)
    	response = getResponseFromDialogflow(usermessage, conversationid)
    	print("userid: %s, conversationid: %s, usermessage: %s, response: %s" %(userid,conversationid,usermessage,response))
    	replyToUser(response,conversationid, userid)

    	conv = {
    		"userIntercomId":userid,
    		"conversationIntercomId":conversationid,
    		"userMessage":usermessage,
    		"responseBot":response,
    		"data": datetime.datetime.utcnow()
    	}

    return "ok"

def getResponseFromDialogflow(usermessage, conversationid):

	# Montando a requisição para a API Dialogflow
	url = "https://api.dialogflow.com/v1/query?v=20150910"

	client_access_token = "..." # Inserir Dialogflow access token

	Headers = {
	    "Authorization":"Bearer "+client_access_token,
	    "Content-Type":"application/json"
	}

	payload = {
	    "lang": "pt-BR",
	    "query": usermessage,
	    "sessionId": "12345",
	    "timezone": "America/New_York"
	}

	r = requests.post(url, data=json.dumps(payload), headers=Headers)
	json_data = json.loads(r.text)
	resposta = json_data["result"]["fulfillment"]["speech"]
	return resposta

def replyToUser(botmessage, conversationid, userid):
	
	# Montando a requisição para a responder ao usuário via API Intercom
	url = 'https://api.intercom.io/conversations/'+conversationid+'/reply'

	access_token = "..." # Inserir Intercom access token

	Headers = {
	    "Authorization":"Bearer "+access_token,
	    "Content-Type":"application/json",
	    "Accept": "application/json"
	}

	payload = {
	  "body": botmessage,
	  "type": "admin",
	  "admin_id": "2061648",
	  "message_type": "comment"
	}

	r = requests.post(url, data=json.dumps(payload), headers=Headers)
	json_data = json.loads(r.text)
	return json_data

def cleanHtmlTags(text):

	# Função para limpar as tags html da mensagem recebida da API Intercom
	clean_text = re.sub('<[^>]+?>', '', text)
	return clean_text

def mongoDbPersist(conv):

	# Estabelecemos a conexão ao Banco de Dados
	conn = MongoClient('localhost', 27017)
	db = conn.conversationsChatbotRedequalis
	collection = db.conversationsChatbotRedequalis

	collection = db.posts
	conv_id = collection.insert_one(conv).inserted_id

	return "ok"

if __name__ == '__main__':
    
	# Rodando API na porta 8000
    port = int(os.getenv('PORT', 8000))
    app.run(debug=True, port=port)