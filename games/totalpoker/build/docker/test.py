#!/usr/bin/env python3
#
# This script accepts environment  variables:
#
#   CONFIGURATE = - on interactive configutation mode
#   CONFIG_OFF_LOGO = - Switch off Total-Game Poker logo
#   CONFIG_DEBUG = - Switch on DEBUG output
#   CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL = 
#   CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL = 
#   CONFIG_PLAYCHAIN_DATABASE_API_PORT = 8500
#   CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT = 8501
#   CONFIG_PLAYCHAIN_DATABASE_P2P_PORT = 10300
#   CONFIG_POKER_ROOM_PORT = 8092
#   CONFIG_POKER_ROOM_CONTROL_PORT = 9100
#   ========================================
#   CONFIG_GENESIS = <path> - Launch RPC with specific genesis JSON (Empty by default)
#   CONFIG_CHAIN_ID = <id> - Empty by default
#   CONFIG_DEBUG_PATH - only for development!
#   CONFIG_TEST_TAG

import sys
import os, os.path as p
import click
import subprocess
import re
import requests as rpc
import json
import socket
import getpass
import atexit
import shutil
import time
import signal
import colorama
import copy

class APP(object):

    def echo_debug(self, data):
        if True:
            click.echo(click.style(">> {}".format(data), fg='white'))
        else:
            pass

    def echo_progress(self, text: str):
        click.echo(click.style("* {}\n".format(text), fg='bright_white'))

    def echo(self, text: str, *args, **kwargs):
        click.echo(click.style(text, fg='bright_white'), *args, **kwargs)
        
    def echo_ok(self, text: str):
        click.echo(click.style(text, fg='green'))

    def echo_warning(self, text: str):
        click.echo(click.style(text, fg='yellow'))

    def echo_error(self, text: str):
        click.echo(click.style(text, fg='red'))

    def test(self):
                    
        args = ["/usr/bin/find"]
        args.append("/");
        args.append("-type");
        args.append("f");
        args.append("-name");
        args.append("boost*");
        
        self.echo_ok("Run {}".format(args))
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.echo_debug("Started subprocess {} pid = {}".format(args[0], proc.pid))
        while True:
            time.sleep(0.1)
            # ln_stderr = str(proc.stderr.readline(), 'utf-8').rstrip()
            ln_stdout = str(proc.stdout.readline(), 'utf-8').rstrip()
            # if any(ln_stderr):
            #     self.echo_warning("STDERR >> {}".format(ln_stderr))
            if any(ln_stdout):
                 self.echo("STDOUT >> {}".format(ln_stdout))
            else:
                break
        self.echo_ok("Finish")
    
app = APP()

def main():
    app.test()
    sys.exit(0)
    
if __name__ == '__main__':
    main()

