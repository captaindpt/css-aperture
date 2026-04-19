"""Shared yt-dlp invocation helpers.

YouTube rolled out aggressive bot-detection in 2026 — most public videos
now return "Sign in to confirm you're not a bot" on every unauthenticated
yt-dlp request, regardless of player_client. The only reliable workaround
(short of running a PO-token provider) is passing cookies from a signed-in
browser session via ``--cookies-from-browser``.

This module centralizes that behavior so every extractor in the codebase
gets the same treatment.

Controlled by environment variables:

``YSS_YT_COOKIES_BROWSER``
    Browser name passed to yt-dlp's ``--cookies-from-browser``.
    Defaults to ``chrome``. Set to ``none`` (or empty) to disable.
    Any value yt-dlp accepts works: ``chrome``, ``firefox``, ``safari``,
    ``edge``, ``brave``, ``chrome:Profile 1``, etc.

``YSS_YT_COOKIES_FILE``
    Path to a Netscape-format cookies.txt exported from a signed-in
    browser session. Takes precedence over ``YSS_YT_COOKIES_BROWSER``
    when set.
"""

from __future__ import annotations

import os
from typing import List


def ytdlp_auth_args() -> List[str]:
    """Return the yt-dlp auth flags based on env configuration.

    Order of precedence:
      1. ``YSS_YT_COOKIES_FILE`` — explicit cookies.txt path.
      2. ``YSS_YT_COOKIES_BROWSER`` — browser to pull cookies from
         (defaults to ``chrome``).
      3. Nothing — returns an empty list.
    """
    cookies_file = os.environ.get("YSS_YT_COOKIES_FILE", "").strip()
    if cookies_file:
        return ["--cookies", cookies_file]

    browser = os.environ.get("YSS_YT_COOKIES_BROWSER", "chrome").strip()
    if not browser or browser.lower() == "none":
        return []

    return ["--cookies-from-browser", browser]


def inject_auth(cmd: List[str]) -> List[str]:
    """Insert auth flags right after the ``yt-dlp`` executable.

    Safe to call on any command list; if the first element isn't
    ``yt-dlp`` the command is returned unchanged.
    """
    if not cmd or cmd[0] != "yt-dlp":
        return cmd

    auth = ytdlp_auth_args()
    if not auth:
        return cmd

    return [cmd[0], *auth, *cmd[1:]]
