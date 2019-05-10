#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import calendar
import datetime
import grpc
import json
import logging
import os
import re
import sys
import time
from threading import Thread

import transitions

from dialog_bot_sdk.bot import DialogBot


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)
logger = logging.getLogger(__name__)


class User:
    """
    1st order states: new, verified (with passport)
    2nd order states are for verified
    """
    _states1 = ['new', 'verified']
    _states2 = ['request', 'subject', 'location', 'meeting', 'bookit', 'modify', 'invitation',
            'passportDetails', 'createGroup']

    def __init__(self, user_id):
        self._id = user_id

    @property
    def id(self):
        return self._id

    def proc(self, msg):
        logger.debug('I am user {} recv msg {}'.format(self.id, msg))
        return 'answer from user {}'.format(self.id)


class NoUserWithId(Exception):
    pass


class UsersPool:
    """
    :param _pool: dict type storage of users
    """
    _pool = dict()
    def __init__(self):
        # you may want to load users from persistant storage here
        pass

    def __del__(self):
        # write pool to storage
        pass

    def recv_from(self, user_id, msg):
        try: # get from memory
            user = self.get_user_by_id(user_id)
        except NoUserWithId:
            try: # get from storage
                user = self.load_user(user_id)
            except NoUserWithId: # create new
                user = self.create_new_user(user_id)
        return user.proc(msg)

    def create_new_user(self, user_id):
        user = User(user_id)
        self._pool[user_id] = user
        return user

    def get_user_by_id(self, user_id):
        try:
            user = self.pool[user_id]
        except KeyError:
            raise NoUserWithId(user_id)
        return user

    def load_user(self, user_id):
        if True: #TODO
            raise NoUserWithId(user_id)
        return user

    @property
    def pool(self):
        return self._pool


users_pool = UsersPool()


def raw_callback(*args, **kwargs):
    """Prevents bot from crashing
    """
    pass


def proc_message(params: tuple):
    """Process message in separate thread
    """
    # check user registered, if not - ask for a passport
    #TODO
    logger.debug('Incoming message:')
    logger.debug('proc_message <- {}'.format(params))
    answer = users_pool.recv_from(params.sender_uid, params)
    bot.messaging.send_message(params.peer, answer)


def incoming_handler(*params):
    """Non-blocking incoming messages stream catcher
    log.debug('Incoming message:')
    for param in params:
        log.debug('message_handler <- {}'.format(param))
    """
    if params[0].peer.id == params[0].sender_uid:
        Thread(target=proc_message, args=(params[0],)).start()
    else:
        logger.debug('peer id not equal sender uid')


if __name__ == '__main__':
    logger.info('starting...')
    SETTINGS_PATH = 'settings.json'


    if os.path.exists(SETTINGS_PATH):
        try: # load settings
            SETTINGS = json.load(open(SETTINGS_PATH))
            TZONE = datetime.datetime.strptime(SETTINGS['timezone'], '%z').tzinfo
        except Exception:
            logger.error("Can't load settings", exc_info=True)
            sys.exit(1)
        logger.debug('Got SETTINGS from {}: {}:'.format(SETTINGS_PATH, str(SETTINGS)))

        try: # init GSuite API
            pass
        except Exception:
            logger.error("Can't initialize Google Calendar API", exc_info=True)
            sys.exit(1)

        try: # init bot
            grpc_endpoint = os.environ.get('GRPC_ENDPOINT')
            if grpc_endpoint.startswith('http'):
                logger.error('gRPC endpoint must start from domain name, remove http* header')
            logger.debug('gRPC endpoint: {}, bot token: {}'
                    .format(grpc_endpoint, os.environ.get('BOT_TOKEN')))
            bot = DialogBot.get_secure_bot(grpc_endpoint,
                    grpc.ssl_channel_credentials(), # empty by default
                    os.environ.get('BOT_TOKEN')
                    )
            bot.messaging.on_message(incoming_handler, raw_callback=raw_callback)
        except Exception:
            logger.error("Can't initialize bot", exc_info=True)
            sys.exit(1)
    else:
        logger.error('{} not found. Create one using "settings_default.json" as a reference'.format(SETTINGS_PATH),
                exc_info=True)
        sys.exit(1)
