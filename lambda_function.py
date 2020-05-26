# -*- coding: utf-8 -*-
"""
Created on Tue May 26 11:10:36 2020

@author: Thomas
"""

from main import main
from json import loads

def lambda_handler(event, context):

    event_body = loads(event['body'])
    message = event_body['message']
    main(message)
