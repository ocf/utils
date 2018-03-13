#!/usr/bin/env python3
import argparse
import hashlib
import re

import requests as r
from ocflib.vhost.web import get_vhosts

missing_img = 'missing_img.log'
missing_disc = 'missing_disc.log'
missing_both = 'missing_both.log'
errors = 'errors.log'
# md5 hashes
banner_hashes = {  # ocfbadge_mini8.png
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
    'a9bfe3f918552692f5eddbd3c5446367',
    # Below hashes are calculated as of 2/18/18
    # berknow150x40.png
    '61cb03fc17cf8a0651627ee78c4801a9',
    # binnov-157x46.png
    '41c167531b66bf22bfcce5f4271b337f',
    # lighter152x41.png
    'a9bfe3f918552692f5eddbd3c5446367',
    # lighter177x48.png
    '774c97d92960c1ac9070c28e0530316b',
    # lighter202x54.png
    'dd65572250059a2bc61f79baa4ee00d6',
    # metal152x41.png
    'abe6c541989915d3e97a2fadd8b84aaf',
    # metal177x48.png
    'a8eff8196bd0e3e3062e2f2526fd92ce',
    # metal202x54.png
    'd56997fc89c6b2fe796a26c291e6de25',
    # ocf-hosted-penguin-dark.png
    '5692198b270c0f86be5b06fe6ac298bd',
    # ocf-hosted-penguin-dark.svg
    '93c79a55e31311628f77e51058c2c0cb',
    # ocf-hosted-penguin.png
    '96304f6f203fa4538f10caeffaea09b5',
    # ocf-hosted-penguin.svg
    '2aaf138a323e9f5a8ee98bafbb5615bf',
    # ocf-hosting-flag-wave-250x122.png
    'ce48822dd63785f77d5826b6b215b18d',
    # ocfbadge_blue8.png
    '0276436d44d1a5e7cfc94b0f2d96907f',
    # ocfbadge_silver8-b.png
    'fc743ade8109379db4ddb2d4cf2723f3',
    # ocfbadge_silver8.png
    'a69a0929a9621638dd5b94161954fa5a'
}

disclaimer_re = 'We\s*are\s*a\s*student\s*group\s*acting\s*independently\s*'\
                'of\s*the\s*University\s*of\s*California.\s*(<[\s\S]*>)?\s*We\s*take\s*full'\
                '\s*responsibility\s*for\s*our\s*organization\s*and\s*this'\
                '\s*web\s*site.'
disclaimer_pattern = re.compile(disclaimer_re)
img_regex = re.compile("=\"?(\S+\.png|\S+\.gif|\S+\.jpg|\S+\.svg)")
special_strings = ['asuc', 'ocf']


def is_special(url_string):
    return any([special_string in url_string for special_string in
                special_strings])


def check_vhosting():
    with open(missing_img, 'w') as m_i, open(missing_disc, 'w') as m_d,\
            open(missing_both, 'w') as m_b, open(errors, 'w') as error_file:
        vhosts = get_vhosts()
        vhost_urls = []
        for vhost_url in vhosts.keys():
            if any(is_special(url) for url in {vhost_url} | set(vhosts[vhost_url]['aliases'])):
                continue
            vhost_urls.append('https://' + vhost_url)
        # For log niceness
        vhost_urls.sort()
        for site in vhost_urls:
            try:
                print('Opening', site)
                siter = r.get(site, timeout=10)
                if siter.status_code == 503:
                    raise Exception('503 Exception')
                site_html = siter.text
                isMissingDisc = False
                if not disclaimer_pattern.search(site_html):
                    isMissingDisc = True
                    m_d.writelines(site + '\n')
                    print('\tNo disclaimer')
                # Check if they have any OCF banner in their images
                img_urls = {img_url if img_url.startswith('http') else site + '/' + img_url for img_url in
                            img_regex.findall(site_html)}
                for img_url in img_urls:
                    # I'm not exactly sure what the deal with \r is but this should work
                    idata = r.get(img_url)
                    img_hash_raw = hashlib.md5(idata.content).hexdigest()
                    img_hash_unix = hashlib.md5(idata.content.replace(b'\r\n', b'\n')).hexdigest()
                    img_hash_window = hashlib.md5(idata.content.replace(b'\n', b'\r\n')).hexdigest()
                    if any([x in banner_hashes for x in [img_hash_raw, img_hash_unix, img_hash_window]]):
                        break
                else:
                    m_i.writelines(site + '\n')
                    print('\tNo banner', img_urls)
                    if isMissingDisc:
                        m_b.writelines(site + '\n')
            except Exception as e:
                print('Error:', e)
                error_file.writelines(site + '\n')
                error_file.writelines(str(e) + '\n\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check if vhost banner and disclaimer exist')
    args = parser.parse_args()
    check_vhosting()
