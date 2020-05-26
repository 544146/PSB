import boto3
import requests
import time
from boto3.dynamodb.conditions import Key, Attr

from TelegramManager import TelegramSender
from ruTorrentFunctions import upload_magnet, upload_torrent, delete_torrent
from TelegramAuth import authorize, add_user
from utilFunctions import needs_argument, get_info_hash_from_torrent, get_info_hash_from_magnet, get_str_added
from jackettFunctions import search_jackett
from plexFunctions import add_plex

def main(message):

    message_text = message['text'].lower()
    is_bot = message['from']['is_bot']

    if is_bot:
        return

    first_name = message['chat']['first_name']
    chat_id = message['chat']['id']
    telegram_manager = TelegramSender(chat_id)

    if not authorize(chat_id):
        if message_text.startswith('/authorize'):
            if needs_argument(message_text):
                telegram_manager.send(
                    'Please enter a password, /authorize {password}')
            elif message_text.split(None, 1)[1] == 'fizz':
                resp_msg = add_user(chat_id, first_name)
                telegram_manager.send(resp_msg)
            else:
                telegram_manager.send(
                    'Invalid password, /authorize {password}')
            return

        telegram_manager.send('Unauthorized, /authorize {password}')
        return

    dynamodb = boto3.resource('dynamodb')
    req_list_db = dynamodb.Table('req-list')
    del_list_db = dynamodb.Table('del-list')

    if message_text.startswith('/search'):

        if needs_argument(message_text):
            telegram_manager.send('You need to provide a query')
            return

        argument = message_text.split(None, 1)[1]
        resp_msg = search_jackett(argument)
        telegram_manager.send(resp_msg)

    elif message_text.startswith('/get'):

        if len(message_text) < 5:
            telegram_manager.send('You need to provide an id')
            return

        an_id = message_text[4:] if needs_argument(
            message_text) else message_text.split(None, 1)[1]

        try:
            int_an_id = int(an_id)
        except ValueError:
            telegram_manager.send('Invalid id')
            return

        if 'Item' not in req_list_db.get_item(Key={'req_id': int_an_id}):
            telegram_manager.send('Nothing to get')
            return

        result = req_list_db.get_item(Key={'req_id': int_an_id})['Item']
        label = result['label']
        title = result['title']
        size = result['size']

        if 'link' in result:
            resReq = requests.get(result['link'])

            if resReq.ok:
                resp_msg = upload_torrent(resReq.content, label)
                telegram_manager.send(resp_msg)#
                
                info_hash = get_info_hash_from_torrent(resReq.content)
            else:
                telegram_manager.send('Error downloading link')

        elif 'magnet' in result:
            resp_msg = upload_magnet(result['magnet'], label)
            telegram_manager.send(resp_msg)
            
            info_hash = get_info_hash_from_magnet(result['magnet'])

        else:
            telegram_manager.send('No link or magnet')
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
            telegram_manager.send('You need to provide an info hash')
            return

        info_hash = message_text[4:] if needs_argument(
            message_text) else message_text.split(None, 1)[1]

        resp_msg = delete_torrent(info_hash)
        telegram_manager.send(resp_msg)
        
        try:
            response = del_list_db.delete_item(Key={'info-hash': info_hash.upper()})
        except ClientError as e:
            pass
        
    elif message_text.startswith('/view'):

        items = del_list_db.query(
            IndexName='chat_id-index',
            KeyConditionExpression=Key('chat_id').eq(chat_id))
        
        resp_msg = get_str_added(items['Items'])
        telegram_manager.send(resp_msg)
        
    elif message_text.startswith('/download'):

        if needs_argument(message_text):
            telegram_manager.send('You need to provide a magnet')
            return

        resp_msg = upload_magnet(message_text.split(None, 1)[1], '')
        telegram_manager.send(resp_msg)

    elif message_text.startswith('/commands') or message_text.startswith(
            '/help'):

        telegram_manager.send(
            '/search {query} (imdb, movie name. etc.)\n' \
            '/get {result_number}\n' \
            '/download {magnet_link}\n' \
            '/authorize {password} e.g. catsanddogs\n' \
            '/add_email {email_address} e.g. g@g.com\n' \
            '/view\n' \
            '/del {info_hash}'
        )

    elif message_text.startswith('/authorize'):

        telegram_manager.send('Already authorized')
        
    elif message_text.startswith('/start'):

        telegram_manager.send('BEEP BOOP STARTING HRRRT do /commands')

    elif message_text.startswith('/add_email'):

        if needs_argument(message_text):
            telegram_manager.send('You need to provide an email')
            return

        argument = message_text.split(None, 1)[1]
        resp_msg = add_plex(argument)
        telegram_manager.send(resp_msg)

    else:

        telegram_manager.send('Invalid command? do /commands')