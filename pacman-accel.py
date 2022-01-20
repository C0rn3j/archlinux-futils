#!/usr/bin/python
#
# A simple local redirector for pacman, to get you the latest packages and
# utilize available mirrors.
#
# Usage:
# - Set multiple mirrors in /etc/pacman.d/mirrorlist-accel with ordering:
# https://fastest-mirror-but-updates-once-a-day/archlinux/
# https://relatively-slower-mirror-that-updates-more-frequently/archlinux/
# ...
# https://pkgbuild-dot-com-or-another-mirror-that-gives-you-the-latest-packages/
#
# - Set /etc/pacman.d/mirrorlist to this redirector:
# Server = http://127.0.0.1:5000/$repo/os/$arch

import logging
import requests
from flask import Flask, redirect

with open("/etc/pacman.d/mirrorlist-accel", "r") as f:
    mirrors = [mirror for mirror in f.read().split('\n')
               if mirror and not mirror[0] == "#"]

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route('/<path:path>')
def download_302(path):
    # Set TIER 0/1 mirrors as the last one, for:
    #  - DB syncing
    #  - Download fallback
    # These two use cases always the same server for consistency.
    mirror = mirrors[-1]

    if not path.endswith('.db'):
        # Find a faster mirror with the requested file present
        for _mirror in mirrors[:-1]:
            response = requests.head(_mirror + path)
            if response.status_code == 200:
                mirror = _mirror
                break
            else:
                app.logger.info('skipping %s for %s, code: %d', _mirror, path, response.status_code)

    app.logger.info('redirecting to %s', mirror + path)
    return redirect(mirror + path, code=302)


if __name__ == '__main__':
   app.run()
