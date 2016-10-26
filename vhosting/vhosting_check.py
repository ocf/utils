#!/usr/bin/python3
import argparse
import re
import urllib.request as req

import ocflib.account.utils as utils
import requests

missing_img = 'missing_img.log'
missing_disc = 'missing_disc.log'
missing_both = 'missing_both.log'
errors = 'errors.log'
banner_urls = ['https://www.ocf.berkeley.edu/hosting-logos/ocfbadge_'
               'mini8.png',
               'https://www.ocf.berkeley.edu/hosting-logos/ocfbadge_'
               'mini8dark.png',
               'https://www.ocf.berkeley.edu/hosting-logos/ocfbadge_'
               'mini8darkglow.png',
               'https://www.ocf.berkeley.edu/hosting-logos/ocfbadge_'
               'platinum.png',
               'https://www.ocf.berkeley.edu/hosting-logos/ocfbadge_'
               'silver8.png',
               'https://www.ocf.berkeley.edu/hosting-logos/ocfbadge_'
               'blue8.png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/binnov-'
               '157x46.gif',
               'https://www.ocf.berkeley.edu/~peterwu/banners/binnov-'
               '157x46.gif.png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/host-ocf.'
               'png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/ocfbadge_'
               'silver-Bkgd.png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/ocfbanner.png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/ocf.png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/ocfbadge_'
               'mini8dark-filtered.jpg',
               'https://www.ocf.berkeley.edu/~peterwu/banners/OX2Ok.png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/OCF-Flag.png',
               'https://www.ocf.berkeley.edu/~peterwu/banners/lighter152x41.'
               'gif.png']
# To-do: Readability
# hosting_logos_prefix = "https://www.ocf.berkeley.edu/hosting-logos/"
# banner_urls = [hosting_logos_prefix + banner_url for banner_url
#                in banner_urls]
# To-do: logs -> small DB
banners = [requests.get(banner_url).content for banner_url in banner_urls]
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
            vhost_urls.append('http://' + vhost_url)
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
                imgs = [requests.get(img_url).content for img_url in
                        img_urls]
                if not any([any([banner == img for img in imgs]) for banner
                            in banners]):
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
