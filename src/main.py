#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python Standard Library
import os
import re
import sys
import grpc
import json
import logging
import datetime
import calendar

# Dialogs Python Bot SDK
from dialog_bot_sdk.bot import DialogBot


# Application specific


# Prevent bot from crashing
def raw_callback(*args, **kwargs):
    pass


def message_handler(*params):
    log.debug('Incoming message:')
    for param in params:
        log.debug('message_handler <- {}'.format(param))


if __name__ == '__main__':
    SETTINGS_PATH = 'settings.json'

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())

    if os.path.exists(SETTINGS_PATH):
        try: # load settings
            SETTINGS = json.load(open(SETTINGS_PATH))
            TZONE = datetime.datetime.strptime(SETTINGS['timezone'], '%z').tzinfo
        except Exception:
            log.error("Can't load settings", exc_info=True)
            sys.exit(1)
        log.debug('Got SETTINGS from {}:\n{}:'.format(SETTINGS_PATH, str(SETTINGS)))

        try: # init GSuite API
            pass
        except Exception:
            log.error("Can't initialize Google Calendar API", exc_info=True)
            sys.exit(1)

        try: # init bot
            grpc_endpoint = os.environ.get('GRPC_ENDPOINT')
            if grpc_endpoint.startswith('http'):
                log.error('gRPC endpoint must start from domain name, remove http* header')
            log.debug('gRPC endpoint: {}, bot token: {}'
                    .format(grpc_endpoint, os.environ.get('BOT_TOKEN')))
            bot = DialogBot.get_secure_bot(grpc_endpoint,
                    grpc.ssl_channel_credentials(), # empty by default
                    os.environ.get('BOT_TOKEN')
                    )
            bot.messaging.on_message(message_handler, raw_callback=raw_callback)
        except Exception:
            log.error("Can't initialize bot", exc_info=True)
            sys.exit(1)
    else:
        log.error('{} not found. Create one using "settings_default.json" as a reference'.format(SETTINGS_PATH),
                exc_info=True)
        sys.exit(1)
