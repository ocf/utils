#!/usr/bin/env python3
import argparse
import socket

import requests as r
from ocflib.vhost.web import get_vhosts

out = 'redirect.log'
errors = 'errors_redir.log'
special_strings = ['asuc', 'ocf']

def striphttp(name):
    return name.split("/")[2]

def is_special(url_string):
    return any([special_string in url_string for special_string in
                special_strings])

def check_vhosting():
    with open(out, 'w') as log, open(errors, 'w') as error_file:
        vhosts = get_vhosts()
        vhost_urls = []
        for vhost_url in vhosts.keys():
            if any(is_special(url) for url in {vhost_url} | set(vhosts[vhost_url]['aliases'])):
                continue
            vhost_urls.append('http://' + vhost_url)
        # For log niceness
        vhost_urls.sort()
        baseIP = socket.gethostbyname('ocf.berkeley.edu')
        for site in vhost_urls:
            try:
                print("Opening", site)
                siter = r.get(site, timeout=10)
                newIP = socket.gethostbyname(striphttp(siter.url))
                if baseIP != newIP:
                    print("\t", newIP)
                    log.writelines(site + "\n")

            except Exception as e:
                print("Error:", e)
                error_file.writelines(site + "\n")
                error_file.writelines(str(e) + '\n\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check redirects on vhosts')
    args = parser.parse_args()
    check_vhosting()
