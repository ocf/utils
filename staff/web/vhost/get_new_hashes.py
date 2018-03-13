#!/usr/bin/env python3
import hashlib
import os

dir = 'images_2-18-2018/'
# Images from ocfweb/ocfweb/static/img/hosting-logos as of 2/18/18

for f in os.listdir(dir):
    with open(dir + f, 'rb') as fp:
        print('#', f, "\n'" + hashlib.md5(fp.read()).hexdigest() + "',")
