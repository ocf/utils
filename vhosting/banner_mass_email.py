#!/usr/bin/python3
import ocflib.account.search as search
import ocflib.misc.mail as mail

vhost_file = '/home/s/st/staff/vhost/vhost.conf'
target_list = 'final_missing_img'

subject = '%s - Missing OCF Banner from Website'
email_body = """Dear %s:

The OCF staff noticed that your group's website [1] does not have the "Hosted
by OCF" banner required by the virtual hosting rules [2]. All student group
websites are required to display the "Hosted by OCF" banner as well as the
student group disclaimer. Unfortunately, if you do not add both of them, we
will be forced to disable your website to comply with the university's
requirements. Please add both sometime within the next 3 weeks (by May 24) to
prevent disabling of your website. Thanks for your cooperation and good luck
on finals.

Your username is "%s".

If you've forgotten how to login, instructions can be found here [3]. If
you've forgotten your password, you can reset it here [4].

Peter Wu
Deputy Manager

1. %s
2. https://www.ocf.berkeley.edu/docs/services/vhost/#h3_including-the-ocf-banner
3. https://www.ocf.berkeley.edu/docs/services/shell/
4. https://www.ocf.berkeley.edu/account/password/
"""

username_site_pairs = []
contact_list = []

with open(target_list) as t_l:
    for line in t_l:
        contact_list.append(line.strip('\n'))

with open(vhost_file) as v_h:
    for line in v_h:
        line = line.strip('\n')
        # Active site
        if (line and not line.startswith('#')):
            # Putting site into right format
            entries = line.split(' ')
            user = entries[0].strip('!')
            if (entries[1] == '-'):
                site = entries[0]
            else:
                site = entries[1]
            site = 'http://' + site.strip('!')
            if '.' not in site:
                site += '.berkeley.edu'
            if site in contact_list:
                username_site_pairs.append((user, site))

# Sanity check
assert len(username_site_pairs) == len(contact_list)

for user, site in username_site_pairs:
    name = search.user_attrs(user)['cn'][0]
    try:
        mail.send_mail_user(user, subject % user, email_body % (name, user, site))
    except Exception as e:
        print((name, user, site, e))
