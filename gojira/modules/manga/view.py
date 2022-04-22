# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo <https://github.com/HitaloSama>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

import asyncio
import math
from typing import Union

import anilist
from pyrogram import filters
from pyrogram.helpers import array_chunk, ikb
from pyrogram.types import CallbackQuery, Message

from gojira.bot import Gojira
from gojira.utils.langs.decorators import use_chat_language


@Gojira.on_message(filters.cmd(r"manga (.+)"))
@Gojira.on_callback_query(filters.regex(r"^manga (\d+)\s?(\d+)?\s?(\d+)?"))
@use_chat_language()
async def manga_view(bot: Gojira, union: Union[CallbackQuery, Message]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    chat = message.chat
    user = union.from_user
    lang = union._lang

    is_private = await filters.private(bot, message)

    query = union.matches[0].group(1)

    if is_callback:
        user_id = union.matches[0].group(2)
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                return

        is_search = union.matches[0].group(3)
        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    async with anilist.AsyncClient() as client:
        if not query.isdecimal():
            results = await client.search(query, "manga", page=1, limit=10)
            if results is None:
                await asyncio.sleep(0.5)
                results = await client.search(query, "manga", page=1, limit=10)

            if results is None:
                return

            if len(results) == 1:
                manga_id = results[0].id
            else:
                keyboard = []
                for result in results:
                    keyboard.append(
                        [(result.title.romaji, f"manga {result.id} {user.id} 1")]
                    )
                await message.reply_text(
                    lang.search_results_text(
                        query=query,
                    ),
                    reply_markup=ikb(keyboard),
                )
                return
        else:
            manga_id = int(query)

        manga = await client.get(manga_id, "manga")

        if manga is None:
            return

        photo: str = ""
        if hasattr(manga, "banner"):
            photo = manga.banner
        elif hasattr(manga, "cover"):
            if hasattr(manga.cover, "extra_large"):
                photo = manga.cover.extra_large
            elif hasattr(manga.cover, "large"):
                photo = manga.cover.large
            elif hasattr(manga.cover, "medium"):
                photo = manga.cover.medium

        text = f"<b>{manga.title.romaji}</b>"
        if hasattr(manga.title, "native"):
            text += f" (<code>{manga.title.native}</code>)"
        text += f"\n\n<b>ID</b>: <code>{manga.id}</code>"
        if (
            hasattr(manga, "score")
            and hasattr(manga.score, "average")
        ):
            text += f"\n<b>{lang.score}</b>: <code>{manga.score.average}</code>"
        text += f"\n<b>{lang.status}</b>: <code>{manga.status}</code>"
        if hasattr(manga, "genres"):
            text += f"\n<b>{lang.genres}</b>: <code>{', '.join(manga.genres)}</code>"
        if hasattr(manga, "volumes"):
            text += f"\n<b>{lang.volume}s</b>: <code>{manga.volumes}</code>"
        if hasattr(manga, "chapters"):
            text += f"\n<b>{lang.chapter}s</b>: <code>{manga.chapters}</code>"
        if not manga.status.lower() == "not_yet_released":
            text += f"\n<b>{lang.start_date}</b>: <code>{manga.start_date.day if hasattr(manga.start_date, 'day') else 0}/{manga.start_date.month if hasattr(manga.start_date, 'month') else 0}/{manga.start_date.year if hasattr(manga.start_date, 'year') else 0}</code>"
        if not manga.status.lower() in ["not_yet_released", "releasing"]:
            text += f"\n<b>{lang.end_date}</b>: <code>{manga.end_date.day if hasattr(manga.end_date, 'day') else 0}/{manga.end_date.month if hasattr(manga.end_date, 'month') else 0}/{manga.end_date.year if hasattr(manga.end_date, 'year') else 0}</code>"

        buttons = [
            (lang.view_more_button, f"manga more {manga.id} {user.id}"),
        ]

        keyboard = array_chunk(buttons, 2)

        if bool(message.photo) and not bool(message.via_bot):
            await message.edit_text(
                text,
                reply_markup=ikb(keyboard),
            )
        else:
            await message.reply_photo(
                photo,
                caption=text,
                reply_markup=ikb(keyboard),
            )


@Gojira.on_callback_query(filters.regex(r"^manga more (\d+) (\d+)"))
@use_chat_language()
async def manga_view_more(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    user = callback.from_user
    lang = callback._lang

    manga_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))

    if user_id != user.id:
        return

    async with anilist.AsyncClient() as client:
        manga = await client.get(manga_id, "manga")

        buttons = [
            (lang.description_button, f"manga description {manga_id} {user_id} 1"),
            (lang.characters_button, f"manga characters {manga_id} {user_id}"),
            (lang.studios_button, f"manga studios {manga_id} {user_id}"),
        ]

        buttons.append(("🐢 Anilist", manga.url, "url"))

        keyboard = array_chunk(buttons, 2)

        keyboard.append([(lang.back_button, f"manga {manga_id} {user_id}")])

        await message.edit_text(
            lang.view_more_text,
            reply_markup=ikb(keyboard),
        )


@Gojira.on_callback_query(filters.regex(r"manga description (\d+) (\d+) (\d+)"))
@use_chat_language()
async def manga_view_description(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    chat = message.chat
    user = callback.from_user
    lang = callback._lang

    manga_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))
    page = int(callback.matches[0].group(3))

    if user_id != user.id:
        return

    async with anilist.AsyncClient() as client:
        manga = await client.get(manga_id, "manga")

        description = manga.description
        amount = 1024
        page = 1 if page <= 0 else page
        offset = (page - 1) * amount
        stop = offset + amount
        pages = math.ceil(len(description) / amount)
        description = description[offset - (3 if page > 1 else 0) : stop]

        page_buttons = []
        if page > 1:
            page_buttons.append(
                ("⬅️", f"manga description {manga_id} {user_id} {page - 1}")
            )
        if not page == pages:
            description = description[: len(description) - 3] + "..."
            page_buttons.append(
                ("➡️", f"manga description {manga_id} {user_id} {page + 1}")
            )

        keyboard = []
        if len(page_buttons) > 0:
            keyboard.append(page_buttons)

        keyboard.append([(lang.back_button, f"manga more {manga_id} {user_id}")])

        await message.edit_text(
            description,
            reply_markup=ikb(keyboard),
        )


@Gojira.on_callback_query(filters.regex(r"^manga characters (\d+) (\d+)"))
@use_chat_language()
async def manga_view_characters(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    chat = message.chat
    user = callback.from_user
    lang = callback._lang

    manga_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))

    if user_id != user.id:
        return

    async with anilist.AsyncClient() as client:
        manga = await client.get(manga_id, "manga")

        keyboard = [
            [
                (lang.back_button, f"manga more {manga_id} {user_id}"),
            ],
        ]

        text = lang.characters_text

        for character in manga.characters:
            text += f"\n• <code>{character.id}</code> - <a href='https://t.me/{bot.me.username}/?start=character_{character.id}'>{character.name.full}</a> (<i>{character.role}</i>)"

        await message.edit_text(
            text,
            reply_markup=ikb(keyboard),
        )


@Gojira.on_callback_query(filters.regex(r"^manga studios (\d+) (\d+)"))
@use_chat_language()
async def manga_view_studios(bot: Gojira, callback: CallbackQuery):
    message = callback.message
    chat = message.chat
    user = callback.from_user
    lang = callback._lang

    manga_id = int(callback.matches[0].group(1))
    user_id = int(callback.matches[0].group(2))

    if user_id != user.id:
        return

    await callback.answer(lang.unfinished_function_alert, show_alert=True)