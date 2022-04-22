# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from typing import Dict, Union

from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"about$"))
@Gojira.on_callback_query(filters.regex(r"^about$"))
@use_chat_language()
async def about(bot: Gojira, union: Union[CallbackQuery, Message]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    lang = union._lang

    kwargs: Dict = {}

    is_private = await filters.private(bot, message)
    if is_private and is_callback:
        keyboard = [
            [
                (lang.back_button, "start"),
            ],
        ]
        kwargs["reply_markup"] = ikb(keyboard)

    await (message.edit_text if is_callback else message.reply_text)(
        lang.about_text.format(
            bot_name=bot.me.first_name,
            github="<a href='https://github.com/HitaloSama/Gojira'>GitHub</a>",
            group=f"<a href='https://t.me/SpamTherapy'>{lang.group}</a>",
        ),
        disable_web_page_preview=True,
        **kwargs,
    )