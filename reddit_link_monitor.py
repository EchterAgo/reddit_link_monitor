#!/usr/bin/env python
# reddit_link_monitor - Monitors reddit for misleading links
# Copyright (C) 2020 Axel Gembe <derago@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
from urllib.parse import urlparse
import logging
from datetime import datetime, timedelta, timezone

import praw
from bs4 import BeautifulSoup

from config import *

logging.basicConfig(format='%(asctime)s %(message)s', level=LOG_LEVEL)

USER_AGENT = 'python:net.loping.reddit_link_monitor:v0.0.1 (by /u/ichundes)'
reddit: praw.Reddit

_link_regex = re.compile(r'^https?:\/\/', re.IGNORECASE)


def alert(source, text, hostname):
    logging.warning(
        f'Found suspicious link in {source.fullname} @ https://reddit.com{source.permalink} !')
    source.report(f'Found suspicious link titled "{text}" pointing to non-official site {hostname}')


def process_html(source, html: str):
    soup = BeautifulSoup(html, features="html.parser")
    for link in soup.findAll('a', attrs={'href': _link_regex}):
        for rule in MONITOR_RULES:
            if rule['regex'].search(link.text):
                hostname = urlparse(link.get('href')).hostname
                if not hostname in rule['official_sites']:
                    alert(source, link.text, hostname)


def process_post(source):
    logging.info(f'Processing {source.fullname}...')
    if isinstance(source, praw.models.Comment):
        if source.body_html:
            process_html(source, source.body_html)
    if isinstance(source, praw.models.Submission):
        if source.is_self and source.selftext_html:
            process_html(source, source.selftext_html)


def get_interesting_items(subreddit, **kwargs):
    results = []

    start_update_time = datetime.now(timezone.utc)

    # Listen for new comments and submissions
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))

    # Filter out comments that can be ninja edited
    def _filter(item):
        item_time = datetime.fromtimestamp(item.created_utc, timezone.utc)
        return start_update_time - item_time > MINIMUM_AGE
    results = [r for r in results if _filter(r)]

    # If we are a moderator of the subreddit, listen to edits.
    # This has to be done by sub as the multi subreddit object can't moderate.
    for sr in REDDIT_SUBS:
        subreddit = reddit.subreddit(sr)
        if REDDIT_USER in subreddit.moderator():
            results.extend(subreddit.mod.edited(**kwargs))

    results.sort(key=lambda post: post.created_utc, reverse=True)

    return results


def main():
    global reddit
    reddit = praw.Reddit(username=REDDIT_USER,
                         password=REDDIT_PASSWORD,
                         client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         user_agent=USER_AGENT)

    def _modify_id(item, id):
        if isinstance(item, praw.models.Comment):
            if item.body:
                id += item.body
        if isinstance(item, praw.models.Submission):
            if item.is_self and item.selftext:
                id += item.selftext
        return id

    subreddit = reddit.subreddit('+'.join(REDDIT_SUBS))
    stream = praw.models.util.stream_generator(
        lambda **kwargs: get_interesting_items(subreddit, **kwargs),
        attribute_function=_modify_id)
    for comment in stream:
        process_post(comment)


if __name__ == "__main__":
    main()
