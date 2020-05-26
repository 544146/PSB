import re
import os
import requests

def add_plex(email):

    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if not (re.search(regex, email)):
        return 'Invalid email'

    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://app.plex.tv',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://app.plex.tv/',
    }

    params = (
        ('X-Plex-Client-Identifier', os.environ['x_plex_client_identifier']),
        ('X-Plex-Token', os.environ['x_plex_token']),
    )

    data = '{"machineIdentifier":"' + os.environ['plex_machine_identifier'] + '","invitedEmail":"' + email + '"}'

    response = requests.post(
        'https://plex.tv/api/v2/shared_servers',
        headers=headers,
        params=params,
        data=data)
    if response.ok:
        return 'Added email'
    elif response.status_code == 422:
        return 'Email already added'

    return 'Something went wrong'