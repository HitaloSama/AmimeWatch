# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from functools import wraps
from typing import Callable, Union

from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import CallbackQuery, InlineQuery, Message

from gojira.database.chats import get_chat_by_id
from gojira.database.users import get_user_by_id
from gojira.utils.langs import chat_languages, get_languages, user_languages

languages = get_languages()
languages = {
    code: languages.get_language(code) for code in get_languages(only_codes=True)
}


def use_chat_language() -> Callable:
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        async def wrapper(
            client: Client, union: Union[CallbackQuery, InlineQuery, Message]
        ) -> Callable:
            message = union.message if isinstance(union, CallbackQuery) else union
            if not isinstance(union, InlineQuery):
                chat = message.chat

            if isinstance(union, InlineQuery) or chat.type == ChatType.PRIVATE:
                user_id = union.from_user.id

                if user_id not in user_languages:
                    user = await get_user_by_id(user_id)
                    if user is None:
                        user_languages[user_id] = "en"
                    else:
                        user_languages[user_id] = user["language"]
                        if user["language"] not in languages:
                            user_languages[user_id] = "en"
                union._lang = languages[user_languages[user_id]]
            else:
                chat_id = chat.id

                if chat_id not in chat_languages:
                    chat = await get_chat_by_id(chat_id)
                    if chat is None:
                        chat_languages[chat_id] = "en"
                    else:
                        chat_languages[chat_id] = chat["language"]
                        if chat["language"] not in languages:
                            chat_languages[chat_id] = "en"
                union._lang = languages[chat_languages[chat_id]]

            return await function(client, union)

        return wrapper

    return decorator
