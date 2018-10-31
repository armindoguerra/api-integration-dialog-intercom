# Workflow do Chatbot

As conversas entre os usuários e o chatbot iniciam-se quando um visitante acessa o chat da Intercom. Nesse momento a API Intercom envia uma notificação para a API de integração informando que existe uma nova conversa. A API de Integração, por sua vez, recebe as informações pertinentes e faz comunicação com a API Dialogflow, onde fica o agente treinado. A API de Integração encarrega-se de enviar a resposta criada pelo Agente Dialogflow para ser apresentada ao usuário que iniciou a conversa. Com intuito de armazenar os dados para análises futuras a API de Integração está preparada para persistir as conversas em um bando de dados NoSQL (Mongodb). 

# Orientações para uso da API

Sugere-se que as etapas sejam realizadas na ordem em que estão apresentadas.

## Pré-requisitos

Necessário para implementação:

- Um usuário administrador da plataforma Intercom;
- Credenciais da conta do Goole que hospeda o chatboot no Dialogflow. 

## Etapa 1 - Chaves de acesso as API's Intercom e Dialogflow

As chaves de acesso utilizadas para testes estão carregadas `hardcoded` (api_integration.py). Para regerá-las é acesse as urls:

1. Intercom - https://app.intercom.com/a/apps/lpl09j4t/developer-hub/app-packages/22870/oauth
2. Dialogflow - Client access token https://console.dialogflow.com/api-client/#/editAgent/61360009-49de-4c9e-b2e9-42d185538107/

## Etapa 2 - Configurar API de Integração e deixá-la disponível

Todas as configurações abaixo devem ser realizadas no arquivo *integration.py*.

1. A Chave de acesso à API Dialoflow fica registrada na função `getResponseFromDialogflow()`;
2. A Chave de acesso à API Intercom fica registrada na função `replyToUser()`;
3. No final da API deve-se informar a porta do servidor que ficará aberta para que a API receba as *requests*;
4. Na função `mongoDbPersist()` deve-se configurar a porta e a url do Mongodb.

Por fim, basta executar a API:

```
$ python integration.py
```    

## Etapa 3 - Criação da webhook na plataforma Intercom

Para criar a webhook na plataforma Intercom é preciso acessar o [link](https://app.intercom.com/a/apps/lpl09j4t/developer-hub/app-packages/22870/messenger-framework) e inserir a url para o servidor onde a API de Integração (**Etapa 2**) estará "escutando" as requisições.

## Etapa 4 - Subscription

Com a API de Integração rodando e com a webhook configurada, é preciso agora informar à API Intercom quais serviços serão monitorados para que a API de Integração receba as notificações e faça as devidas integrações. A Intercom denomina essa etapa como *subscription*. Serão inicializados 2 serviços:

- Quando uma conversa dor iniciada/criada: `conversation.user.created`;
- Quando um usuário responder: `conversation.user.replied`.

Além da incialização dos serviços, outra informção importante que também é enviada nessa *subscription* é a *URL* que ficará *escutando* as notificações, a mesma configurada na **Etapa 3**. 

Segue um exemplo de subscription estruturada para ser enviada usando *CURL*. 

```
curl "https://api.intercom.io/subscriptions/nsub_93e85980-90f7-11e8-8cf1-67508c200d87" 

-XPOST -H 'Authorization:Bearer [api key Intercom]' 
-H 'Accept: application/json' 
-H 'Content-Type: application/json' 
-d '{
		"service_type": "web",
		"topics": 
			[
				"conversation.user.replied",
				"conversation.user.created"
			],
		"url": "https:..." 
	}'
```

A lista completa de todos os serviços que podem ser inicializados pode ser encontrada em https://developers.intercom.com/intercom-api-reference/reference na seção WEBHOOKS -> Topics.



