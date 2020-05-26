from main import main
from json import loads

def lambda_handler(event, context):

    event_body = loads(event['body'])
    message = event_body['message']
    main(message)
