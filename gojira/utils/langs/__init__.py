"""Gojira langs utilities."""
# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2022 Hitalo M. <https://github.com/HitaloM>
# Copyright (c) 2021 Andriel <https://github.com/AndrielFR>

from typing import Dict, List

from .core import Langs
from .load_langs import get_languages, load_languages

chat_languages: Dict = {}
user_languages: Dict = {}

__all__: List[str] = ["Langs", "get_languages", "load_languages"]
