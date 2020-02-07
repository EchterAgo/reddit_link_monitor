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

# Copy this file to config.py and edit it.

import re
import logging
from datetime import timedelta

LOG_LEVEL = logging.WARNING

REDDIT_USER = ''
REDDIT_PASSWORD = ''

REDDIT_CLIENT_ID = ''
REDDIT_CLIENT_SECRET = ''

# Do not process items until they have reached the ninja edit limit
# See https://www.reddit.com/r/NoStupidQuestions/comments/33qgq7/how_long_do_you_have_to_edit_a_reddit_comment/
MINIMUM_AGE = timedelta(seconds=180)

REDDIT_SUBS = [
    'btc',
    'Bitcoincash'
]

MONITOR_RULES = [
    {
        # Regex matching the link titles that should be matched
        'regex': re.compile(r'electr(um|on)', re.IGNORECASE),
        # List of acceptable official domains, all lowercase
        'official_sites': [
            'electroncash.org',
            'electrum.org',
            'electrumsv.io'
        ]
    }
]
