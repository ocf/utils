#!/usr/bin/python2.7
"""
Bludgeon our way into a working WordPress install.

Requirements:
    1. Check for root.
    2. makehttp
    3. makemysql
    4. Drop tables
    5. Download WordPress
    6. Config WordPress
    6.5. Prompt for and save user credentials
    7. Install WordPress
    8. Install ``Disable Comments'' plugin
"""

import argparse
import getpass
import os
import re
import sys
from subprocess import check_output

# Load it in main
update = None

class Bludgeon(object):
    pass

class MysqlWrapper(object):
    MATCH = re.compile(r">>> Your MySQL database password is: (?P<pass>.*)")

    def __init__(self):
        self.password = None

    def reset_password(self, user, recreate_database=True):
        out = check_output("echo yes | makemysql", shell=True)
        res = self.MATCH.search(out)
        self.password = res.groupdict()['pass']

        if recreate_database:
            check_output(
                "echo drop database {user} | mysql -p{password}".format(
                    user=user,
                    password=self.password,
                ),
                shell=True,
            )
            check_output(
                "echo create database {user} | mysql -p{password}".format(
                    user=user,
                    password=self.password,
                ),
                shell=True,
            )
    def disable_comments(self, user):
        """Black magic MySQL incantations.

        The query is:
            REPLACE INTO `wp_options` (`option_name`, `option_value`, `autoload`) VALUES ('disable_comments_options','a:4:{s:19:\"disabled_post_types\";a:3:{i:0;s:4:\"post\";i:1;s:4:\"page\";i:2;s:10:\"attachment\";}s:17:\"remove_everywhere\";b:1;s:9:\"permanent\";b:0;s:10:\"db_version\";i:5;}','yes');
        but I can't deal with the escaping.
        """
        check_output(
            "echo UkVQTEFDRSBJTlRPIGB3cF9vcHRpb25zYCAoYG9wdGlvbl9uYW1lYCwgYG9wdGlvbl92YWx1ZWAsIGBhdXRvbG9hZGApIFZBTFVFUyAoJ2Rpc2FibGVfY29tbWVudHNfb3B0aW9ucycsJ2E6NDp7czoxOTpcImRpc2FibGVkX3Bvc3RfdHlwZXNcIjthOjM6e2k6MDtzOjQ6XCJwb3N0XCI7aToxO3M6NDpcInBhZ2VcIjtpOjI7czoxMDpcImF0dGFjaG1lbnRcIjt9czoxNzpcInJlbW92ZV9ldmVyeXdoZXJlXCI7YjoxO3M6OTpcInBlcm1hbmVudFwiO2I6MDtzOjEwOlwiZGJfdmVyc2lvblwiO2k6NTt9JywneWVzJyk7 | base64 -d | mysql -p{password} {user}".format(
                password=self.password,
                user=user,
            ),
            shell=True,
        )


class WpCliWrapper(object):
    class Module(object):
        def __init__(self, parent, name):
            self.parent = parent
            self.name = name

        def _call(self, action_name, *args, **kwargs):
            self.parent._call(self.name, action_name, *args, **kwargs)

        def __getattr__(self, name):
            def callable(*args, **kwargs):
                self._call(name, *args, **kwargs)
            return callable

    def __init__(self):
        self.wpcli_bin = os.path.join(script_basename, "wp-cli.phar")

    def _call(self, mod_name, action_name, *args, **kwargs):
        kwargs = [
            "--{option_name}=\"{option_value}\"".format(
                option_name=option_name,
                option_value=option_value,
            )
            for option_name, option_value in kwargs.items()
        ]
        kwargs = " ".join(kwargs)
        if any(kwargs):
            kwargs = " " + kwargs

        args = " ".join(map(str, args))
        if any(args):
            args = " " + args

        cmd = "{bin} {module} {action}{kwargs}{args}".format(
            bin=self.wpcli_bin,
            module=mod_name,
            action=action_name,
            kwargs=kwargs,
            args=args,
        )
        print cmd
        print check_output(cmd, shell=True)

    def __getattr__(self, name):
        """Create a callable which proxies through to WP-CLI.
        """
        return WpCliWrapper.Module(self, name)

def prompt(prompt_tuples):
    def input_func(key):
        if 'pass' in key:
            return getpass.getpass
        return raw_input

    prompt = dict(prompt_tuples)
    responses = {}
    for key, desc in prompt.items():
        responses[key] = input_func(key)(desc + ": ")

    return responses

def main():
    parser = argparse.ArgumentParser(description="Bludgeon our way into a working WordPress install.")
    parser.add_argument("-u", "--user", type=str, required=True)

    args = parser.parse_args()


    # I am going to fix the admin user as "admin" to avoid confusion with
    # student group succession...
    prompt_for = (
        ("admin_email", "Admin email address"),
        ("admin_pass", "Admin user's password"),
        ("full_url", "Full URL of site"),
        ("site_name", "Site name"),
    )

    results = prompt(prompt_for)

    wp = WpCliWrapper()
    mysql = MysqlWrapper()

    mysql.reset_password(args.user)

    wp.core.download()
    wp.core.config(dbname=args.user, dbuser=args.user, dbpass=mysql.password, dbhost="mysql")
    wp.core.install(url=results['full_url'], title=results['site_name'], admin_user="admin", admin_password=results['admin_pass'], admin_email=results['admin_email'])
    wp.plugin.install("disable-comments")
    wp.plugin.activate("disable-comments")

    mysql.disable_comments(args.user)

if __name__ == "__main__":
    script_basename = os.path.dirname(os.path.realpath(__file__))

    main()
