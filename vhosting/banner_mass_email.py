#!/usr/bin/python3
import argparse

import ocflib.account.search as search
import ocflib.account.utils as utils
import ocflib.misc.mail as mail

subject = '{user} - Missing OCF Banner from Website'
# Warning: Email is date-specific and only makes sense once a year.
email_body = """Dear {user}:

The OCF staff noticed that your group's website [1] does not have the "Hosted
by OCF" banner required by the virtual hosting rules [2]. All student group
websites are required to display the "Hosted by OCF" banner as well as the
student group disclaimer. Unfortunately, if you do not add both of them, we
will be forced to disable your website to comply with the university's
requirements. Please add both sometime within the next 3 weeks (by May 24) to
prevent disabling of your website. Thanks for your cooperation and good luck
on finals.

Your username is {name}.

If you've forgotten how to login, instructions can be found here [3]. If
you've forgotten your password, you can reset it here [4].

Thanks for flying OCF,
The friendly staff of 171 MLK Student Union

1. {site}
2. https://www.ocf.berkeley.edu/docs/services/vhost/#h3_including-the-ocf-banner
3. https://www.ocf.berkeley.edu/docs/services/shell/
4. https://www.ocf.berkeley.edu/account/password/
"""


def send_mass_mail(target_log, dry_run):
    username_site_pairs = []
    contact_list = []
    with open(target_log) as t_l:
        for line in t_l:
            contact_list.append(line.strip('\n'))

    vhosts = utils.get_vhosts()
    for vhost_url in vhosts.keys():
        site = 'http://' + vhost_url
        if site in contact_list:
            username_site_pairs.append((vhosts[vhost_url]['username'],
                                        vhost_url))

    # Sanity check
    assert len(username_site_pairs) == len(contact_list)

    if not dry_run:
        print('Emailing...')
        for user, site in username_site_pairs:
            name = search.user_attrs(user)['cn'][0]
            try:
                print(user)
                mail.send_mail_user(user, subject.format(user=user),
                                    email_body.format(user=user, name=name, site=site))
            except Exception as e:
                print((name, user, site, e))
    else:
        print("Actual run would've emailed the following:")
        for user, site in username_site_pairs:
            print(user)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check if vhost banner and '
                                     'disclaimer exist')
    parser.add_argument('target_log', type=str, nargs='+',
                        help='Log file (list of websites) to email')
    parser.add_argument('--actual', nargs='?', const=1, default=0,
                        help='Run script as not a dry-run')

    args = parser.parse_args()
    send_mass_mail(args.target_log[0], not args.actual)
