import boto3
import os

def is_authorized(chat_id):
    dynamodb = boto3.resource('dynamodb')
    bot_auth_db = dynamodb.Table('plex-auth')
    return "Item" in bot_auth_db.get_item(Key={'chat_id': chat_id})

def authorize(password):
    return password == os.environ['telegram_password']

def add_user(chat_id, first_name):
    dynamodb = boto3.resource('dynamodb')
    bot_auth_db = dynamodb.Table('plex-auth')

    if 'Item' not in bot_auth_db.get_item(Key={'chat_id': chat_id}):
        bot_auth_db.put_item(Item={
            'chat_id': chat_id,
            'first_name': first_name
        })
        return 'Authorization successful'

    return 'Already authorized'
