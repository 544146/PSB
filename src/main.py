import boto3
import requests
import time
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import Telegram
import ruTorrent
import Authorization
import Jackett
import Plex
from utils import *

def main(message):

    message_text = message['text'].lower()
    is_bot = message['from']['is_bot']

    if is_bot:
        return

    first_name = message['chat']['first_name']
    chat_id = message['chat']['id']
   
    telegram_sender = Telegram.Sender(chat_id)

    if not Authorization.is_authorized(chat_id):
        if message_text.startswith('/authorize'):
            if needs_argument(message_text):
                telegram_sender.send(
                    'Please enter a password, /authorize {password}')
            elif Authorization.authorize(message_text.split(None, 1)[1]):
                resp_msg = Authorization.add_user(chat_id, first_name)
                telegram_sender.send(resp_msg)
            else:
                telegram_sender.send(
                    'Invalid password, /authorize {password}')
            return
        
        elif message_text.startswith('/start'):
            telegram_sender.send(
                'BEEP BOOP STARTING HRRRT do /authorize {password}')
            return
        
        telegram_sender.send('Unauthorized, /authorize {password}')
        return

    dynamodb = boto3.resource('dynamodb')
    req_list_db = dynamodb.Table('req-list')
    del_list_db = dynamodb.Table('del-list')

    if message_text.startswith('/search'):

        if needs_argument(message_text):
            telegram_sender.send('You need to provide a query')
            return

        msg = telegram_sender.send("Searching...")
        msg_id = msg.json()['result']['message_id'] 
        argument = message_text.split(None, 1)[1]
        resp_msg = Jackett.search(argument)
        telegram_sender.edit(resp_msg, msg_id)

    elif message_text.startswith('/get'):

        if len(message_text) < 5:
            telegram_sender.send('You need to provide an id')
            return

        an_id = message_text[4:] if needs_argument(
            message_text) else message_text.split(None, 1)[1]

        try:
            int_an_id = int(an_id)
        except ValueError:
            telegram_sender.send('Invalid id')
            return

        if 'Item' not in req_list_db.get_item(Key={'req_id': int_an_id}):
            telegram_sender.send('Nothing to get')
            return

        result = req_list_db.get_item(Key={'req_id': int_an_id})['Item']
        label = result['label']
        title = result['title']
        size = result['size']

        if 'magnet' in result:
            resp_msg = ruTorrent.upload_magnet(result['magnet'], label)
            telegram_sender.send(resp_msg)
            
            info_hash = get_info_hash_from_magnet(result['magnet'])
            
        elif 'link' in result:
            
            resReq = requests.get(result['link'], allow_redirects=False)

            try:
                if resReq.status_code == 302:
                    resp_msg = ruTorrent.upload_magnet(resReq.headers['Location'], label)
                    telegram_sender.send(resp_msg)
            
                    info_hash = get_info_hash_from_magnet(resReq.headers['Location'])
                    
                elif resReq.ok:
                    resp_msg = ruTorrent.upload_torrent(resReq.content, label)
                    telegram_sender.send(resp_msg)
                
                    info_hash = get_info_hash_from_torrent(resReq.content)
                    
                else:
                    telegram_sender.send('Error downloading link')
                    return
                
            except:
                telegram_sender.send('Error, something went wrong')
                return

        else:
            telegram_sender.send('No link or magnet')
            return
        
        del_list_db.put_item(
            Item={
                'info-hash': info_hash.upper(),
                'chat_id': chat_id,
                'label': label,
                'title': title,
                'size': size,
                'added': int(time.time())
            })
            
    elif message_text.startswith('/del'):

        if len(message_text) < 5:
            telegram_sender.send('You need to provide an info hash')
            return

        info_hash = message_text[4:] if needs_argument(
            message_text) else message_text.split(None, 1)[1]

        resp_msg = ruTorrent.delete_torrent(info_hash)
        telegram_sender.send(resp_msg)
        
        try:
            response = del_list_db.delete_item(Key={'info-hash': info_hash.upper()})
        except ClientError as e:
            pass
        
    elif message_text.startswith('/view'):

        items = del_list_db.query(
            IndexName='chat_id-index',
            KeyConditionExpression=Key('chat_id').eq(chat_id))
        
        resp_msg = get_str_added(items['Items'])
        telegram_sender.send(resp_msg)
        
    elif message_text.startswith('/download'):

        if needs_argument(message_text):
            telegram_sender.send('You need to provide a magnet')
            return

        resp_msg = ruTorrent.upload_magnet(message_text.split(None, 1)[1], '')
        telegram_sender.send(resp_msg)

    elif message_text.startswith('/commands') or message_text.startswith(
            '/help'):

        telegram_sender.send(
            '/search {query} (imdb, movie name. etc.)\n' \
            '/get {result_number}\n' \
            '/download {magnet_link}\n' \
            '/authorize {password} e.g. catsanddogs\n' \
            '/add_email {email_address} e.g. g@g.com\n' \
            '/view\n' \
            '/del {info_hash}'
        )

    elif message_text.startswith('/authorize'):

        telegram_sender.send('Already authorized')
        
    elif message_text.startswith('/start'):

        telegram_sender.send('BEEP BOOP STARTING HRRRT do /commands')

    elif message_text.startswith('/add_email'):

        if needs_argument(message_text):
            telegram_sender.send('You need to provide an email')
            return

        argument = message_text.split(None, 1)[1]
        resp_msg = Plex.add_email(argument)
        telegram_sender.send(resp_msg)

    else:

        telegram_sender.send('Invalid command? do /commands')
