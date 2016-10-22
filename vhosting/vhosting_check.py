#!/usr/bin/python3

import argparse
import urllib.request as req
import os, re, requests, sys

banners_dir = "./banners/"
logs_dir = "./logs/"
missing_img = logs_dir + "missing_img.log"
missing_disc = logs_dir + "missing_disc.log"
missing_both = logs_dir + "missing_both.log"
errors = logs_dir + "errors.log"
# To-do: logs -> small DB
banners = [open(banners_dir + entry, "rb").read() for entry in
           os.listdir("./banners")]
disclaimer = "We are a student group acting independently of the University"\
             " of California. We take full responsibility for our"\
             " organization and this web site."
img_regex = re.compile("=\"?(\S+\.png|\S+\.gif|\S+\.jpg)")
special_strings = ["asuc", "ocf"]

def is_special(url_string):
    # To-do: Read from log of known exceptionsk
    # if url_string in exceptions:
    #     return True
    return any([special_string in url_string for special_string in 
                special_strings])

def check_vhosting(vhost_file):
    with open(vhost_file, "r") as vh, open(missing_img, "w") as m_i, \
         open(missing_disc, "w") as m_d, open(missing_both, "w") as m_b, \
         open(errors, "w") as error_file:
        vhosts = []
        for line in vh:
            line = line.strip("\n")
            # Active site
            if (line and not line.startswith("#") and not is_special(line)):
                # Putting site into right format
                entries = line.split(" ")
                if (entries[1] == "-"):
                    site = entries[0]
                else:
                    site = entries[1]
                site = "http://" + site.strip("!")
                if "." not in site:
                    site += ".berkeley.edu"
                site += "\n"
                try:
                    site_opened = req.urlopen(site, timeout=10)
                    site_html = site_opened.readall().decode("utf-8")
                    counter = 0
                    if disclaimer not in site_html:
                        counter += 1
                        m_d.writelines(site)
                    # Check if they have any OCF banner in their images
                    img_urls = [img_url if img_url.startswith("http") else
                                site + "/" + img_url for img_url in
                                img_regex.findall(site_html)]
                    imgs = [requests.get(img_url).content for img_url in
                            img_urls]
                    if not any([any([banner == img for img in imgs]) for banner
                                in banners]):
                        m_i.writelines(site)
						if counter == 1:
							m_b.writelines(site)
                except Exception as e:
                    error_file.writelines(site)
                    error_file.writelines(str(e) + "\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if vhost banner and "
    "disclaimer exist")
    parser.add_argument("vhost_file", type=str, nargs="+",
                        help="OCF vhost file location")
    args = parser.parse_args()
    check_vhosting(args.vhost_file[0])

