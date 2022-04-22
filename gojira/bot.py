# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import datetime
import logging

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram.types import User

import gojira
from gojira.config import API_HASH, API_ID, BOT_TOKEN, SUDO_USERS
from gojira.utils import modules
from gojira.utils.langs import get_languages, load_languages

logger = logging.getLogger(__name__)


class Gojira(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            session_name=name,
            app_version=f"Gojira v{gojira.__version__}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            parse_mode="html",
            workers=24,
            workdir="gojira",
            sleep_threshold=180,
        )

        self.sudos = SUDO_USERS

        self.start_datetime = datetime.datetime.now().replace(
            tzinfo=datetime.timezone.utc
        )

    async def start(self):
        await super().start()

        # Load the languages
        load_languages()
        languages = len(get_languages(only_codes=True))
        logger.info("%s languages was loaded.", languages)

        self.me = await self.get_me()
        logger.info(
            "Gojira running with Pyrogram v%s (Layer %s) started on @%s. Hi!",
            __version__,
            layer,
            self.me.username,
        )

        modules.load(self)

    async def stop(self):
        await super().stop()
        logger.warning("Gojira stopped. Bye!")

    def is_sudo(self, user: User) -> bool:
        return user.id in self.sudos
