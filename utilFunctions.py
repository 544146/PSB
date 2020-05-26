import boto3
import time
import random
import bencodepy
import hashlib
import re

def get_info_hash_from_magnet(magnet_link):
    try:
        return re.search(r'([a-fA-F\d]{40})', magnet_link).group(1)
    except AttributeError:
        return 'error'

def get_info_hash_from_torrent(torrent_file):
    metadata = bencodepy.decode(torrent_file)
    return hashlib.sha1(bencodepy.encode(metadata)).hexdigest()

def get_str_added(items):
    return_string = ''

    if len(items) < 1:
        return 'Nothing to view'
    
    for i in items:

        added = time.strftime('%H:%M:%S %d-%m-%Y', time.localtime(i['added']))
        if not (int(i['added']) + 1296000 > int(time.time()) and i['label'] == 'IPTorrents'):
            return_string += '/del{} - '.format(i['info-hash'])

        return_string += '{}, Added: {}, Size: {}GB'.format(i['label'], added, i['size'])
        return_string += '\n{}\n\n'.format(i['title'])

    return "{}(please don't delete IPTorrents until 2 wks old)".format(return_string)

def get_str_results(results):
    dynamodb = boto3.resource('dynamodb')
    req_list_db = dynamodb.Table('req-list')

    return_string = ''
    sort_by_seeders = sorted(results, key=lambda k: k['Seeders'], reverse=True)

    result_counter = 0
    for r in reversed(sort_by_seeders[:25]):

        req_id = random.randint(10000, 99999)
        count = 0
        while "Item" in req_list_db.get_item(Key={
                "req_id": req_id
        }) and count < 5:
            req_id = random.randint(10000, 99999)

            count += 1
            if count > 4:
                return "Request database is somehow full?..."

        if r['Seeders'] > 0:
            if r['MagnetUri'] is not None:
                req_list_db.put_item(
                    Item={
                        'req_id': req_id,
                        'magnet': r['MagnetUri'],
                        'label': r['Tracker'],
                        'title': r['Title'],
                        'size' : str(round((r['Size'] / 1024 / 1024 / 1024), 2)),
                        'expire': int(time.time() + 3600)
                    })
            elif r['Link'] is not None:
                req_list_db.put_item(
                    Item={
                        'req_id': req_id,
                        'link': r['Link'],
                        'label': r['Tracker'],
                        'title': r['Title'],
                        'size' : str(round((r['Size'] / 1024 / 1024 / 1024), 2)),
                        'expire': int(time.time() + 3600)
                    })
            else:
                continue

            result_counter += 1
            return_string += '/get{} - {}, Seeds: {}, Peers: {}, Size: {}GB'.format(
                str(req_id), r['Tracker'], str(r['Seeders']), str(r['Peers']),
                str(round((r['Size'] / 1024 / 1024 / 1024), 2)))
            return_string += '\n{}\n\n'.format(r['Title'])

    return "Results ({}/{})\n\n{}".format(
        str(result_counter), str(len(results)), return_string)


def needs_argument(message_text):
    return len(message_text.split()) < 2