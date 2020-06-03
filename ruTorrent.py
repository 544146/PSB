import os
import requests
import bencodepy
import urllib

def delete_torrent(del_hash):

    headers = {
        'Authorization': 'Basic {}'.format(os.environ['rutorrent_basic'])
    }

    data = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data><value><struct><member><name>methodName</name><value><string>d.custom5.set</string></value></member><member><name>params</name><value><array><data><value><string>{hash}</string></value><value><string>1</string></value></data></array></value></member></struct></value><value><struct><member><name>methodName</name><value><string>d.delete_tied</string></value></member><member><name>params</name><value><array><data><value><string>{hash}</string></value></data></array></value></member></struct></value><value><struct><member><name>methodName</name><value><string>d.erase</string></value></member><member><name>params</name><value><array><data><value><string>{hash}</string></value></data></array></value></member></struct></value></data></array></value></param></params></methodCall>'.format(hash=del_hash)

    response = requests.post(os.environ['rutorrent_rpc'], headers=headers, data=data)
    
    resp_xml = response.content.decode('utf-8')
    
    if response.ok:
        if 'Could not find info-hash.' in resp_xml:
            return 'Could not find info hash'
        elif 'Unsupported target type found.' in resp_xml:
            return 'Invalid info hash'
        
        return 'Successfully deleted'
        
    return 'Error: {}'.format(response.status_code)


def upload_torrent(torrent_file, label):
    
    metadata = bencodepy.decode(torrent_file)
    file_name = urllib.parse.quote(metadata[b'info'][b'name'].decode())

    params = {'label': label}

    headers = {
        'Authorization': 'Basic {}'.format(os.environ['rutorrent_basic'])
    }

    files = {'torrent_file': (file_name, torrent_file)}

    response = requests.post(
        os.environ['rutorrent_url'],
        headers=headers,
        files=files,
        params=params)

    if response.status_code == 200:
        return response.url[76:].split("&")[0]

    return 'Error: {}'.format(response.status_code)


def upload_magnet(magnet_link, label):

    data = {'url': magnet_link}

    params = {'label': label}

    response = requests.post(
        os.environ['rutorrent_url'], params=params, data=data)
    if response.ok:
        return response.url[76:].split('&')[0]

    return response.status_code