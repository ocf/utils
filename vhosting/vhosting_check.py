#!/usr/bin/python3
import argparse
import hashlib
import re
import urllib.request as req

import ocflib.account.utils as utils
import requests

missing_img = 'missing_img.log'
missing_disc = 'missing_disc.log'
missing_both = 'missing_both.log'
errors = 'errors.log'
# md5 hashes
banner_hashes = [  # ocfbadge_mini8.png
    'b23ee41fdc537191381684dd826cf77f',
    # ocfbadge_mini8dark.png
    'c425451be5b2697bebe4dae12730ce8a',
    # ocfbadge_mini8darkglow.png
    'deaad890013a1ced05aef9ec9d023880',
    # ocfbadge_platinum.png
    'b1bbe54f1b85543b2e9ebb97faa43347',
    # ocfbadge_silver8.png
    'a69a0929a9621638dd5b94161954fa5a',
    # ocfbadge_blue8.png
    '0276436d44d1a5e7cfc94b0f2d96907f',
    # binnov-157x46.gif
    'e21bdc91cd32bc159583215168df3e14',
    # binnov-157x46.gif.png
    '41c167531b66bf22bfcce5f4271b337f',
    # host-ocf.png
    'fbd917bafa6125067ea5c0bc0bb9e912',
    # ocfbadge_silver-Bkgd.png
    '191d1cffd592558d6b748e2cbab2304b',
    # ocfbanner.png
    '46051228558531136e030bce1c45d67b',
    # ocf.png
    'b23ee41fdc537191381684dd826cf77f',
    # ocfbadge_mini8dark-filtered.jpg
    '0779ac671caee34f00887ad2222d6942',
    # OX2Ok.png
    '61a879bd09045605530fb5fc67b1ce9f',
    # OCF-Flag.png
    'ce48822dd63785f77d5826b6b215b18d',
    # lighter152x41.gif.png
    'a9bfe3f918552692f5eddbd3c5446367']
# To-do: Readability
# hosting_logos_prefix = "https://www.ocf.berkeley.edu/hosting-logos/"
# banner_urls = [hosting_logos_prefix + banner_url for banner_url
#                in banner_urls]
# To-do: logs -> small DB
disclaimer = 'We are a student group acting independently of the University'\
             ' of California. We take full responsibility for our'\
             ' organization and this web site.'
img_regex = re.compile("=\"?(\S+\.png|\S+\.gif|\S+\.jpg)")
special_strings = ['asuc', 'ocf']


def is_special(url_string):
    # To-do: Read from log of known exceptions
    # if url_string in exceptions:
    #     return True
    return any([special_string in url_string for special_string in
                special_strings])


def check_vhosting():
    with open(missing_img, 'w') as m_i, open(missing_disc, 'w') as m_d,\
            open(missing_both, 'w') as m_b, open(errors, 'w') as error_file:
        vhosts = utils.get_vhosts()
        vhost_urls = []
        for vhost_url in vhosts.keys():
            if is_special(vhost_url) or any([is_special(alias) for alias in
                                             vhosts[vhost_url]['aliases']]):
                continue
            vhost_urls.append('http://' + vhost_url + '\n')
        # For log niceness
        vhost_urls.sort()
        for site in vhost_urls:
            try:
                site_opened = req.urlopen(site, timeout=10)
                site_html = site_opened.readall().decode('utf-8')
                counter = False
                if disclaimer not in site_html:
                    counter = True
                    m_d.writelines(site)
                # Check if they have any OCF banner in their images
                img_urls = [img_url if img_url.startswith('http') else
                            site + '/' + img_url for img_url in
                            img_regex.findall(site_html)]
                img_hashes = [hashlib.md5(requests.get(img_url).content)
                              .hexdigest() for img_url in img_urls]
                if not any([any([banner_hash == img_hash for img_hash in
                                 img_hashes])
                            for banner_hash in banner_hashes]):
                    m_i.writelines(site)
                    if counter:
                        m_b.writelines(site)
            except Exception as e:
                error_file.writelines(site)
                error_file.writelines(str(e) + '\n\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check if vhost banner and '
                                     'disclaimer exist')
    args = parser.parse_args()
    check_vhosting()
