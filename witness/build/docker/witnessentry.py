#!/usr/bin/env python3
#
# This script accepts environment  variables:
#
#   CONFIGURATE = False - on interactive configutation mode
#   CONFIG_OFF_LOGO = False - Switch off Playchain logo
#   CONFIG_DEBUG = False - Switch on DEBUG output
#   CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL = 
#   CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL = 
#   CONFIG_PLAYCHAIN_DATABASE_API_PORT = 8510
#   CONFIG_PLAYCHAIN_DATABASE_P2P_PORT = 10310
#   ========================================
#   CONFIG_GENESIS = <path> - Launch RPC with specific genesis JSON (Empty by default)
#   CONFIG_CHAIN_ID = <id> - Empty by default
#   CONFIG_DEBUG_PATH - only for development!

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
    PLAYCHAIN_SETUP_CONFIG_FILE_NAME = "playchain.setup.config.ini"
    PLAYCHAIN_RUN_CONFIG_FILE_NAME = "playchain.config.ini"
    PLAYCHAIN_SETUP_FILE_NAME = "playchain.config.template.ini"
    GENESIS_FILE_NAME = "genesis.json"
    PAGE_SIZE = 5
    NEW_ROOM = "new"
    NEXT_ROOM = "next"
    DEFAULT_ROOM = "default"
    PROGRESSBAR_TEXT = "Wait:"
    PROGRESSBAR_BAR_WIDTH = 51
    
    def print_environment(self):
        self.echo_debug("* ROOMENTRY.PY")
        self.echo_debug("CONFIGURATE={}".format(os.environ.get('CONFIGURATE')))
        self.echo_debug("CONFIG_OFF_LOGO={}".format(os.environ.get('CONFIG_OFF_LOGO')))
        self.echo_debug("CONFIG_DEBUG={}".format(os.environ.get('CONFIG_DEBUG')))
        self.echo_debug("CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL={}".format(os.environ.get('CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL')))
        self.echo_debug("CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL={}".format(os.environ.get('CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL')))
        self.echo_debug("CONFIG_PLAYCHAIN_DATABASE_API_PORT={}".format(os.environ.get('CONFIG_PLAYCHAIN_DATABASE_API_PORT')))
        self.echo_debug("CONFIG_PLAYCHAIN_DATABASE_P2P_PORT={}".format(os.environ.get('CONFIG_PLAYCHAIN_DATABASE_P2P_PORT')))
        self.echo_debug("CONFIG_GENESIS={}".format(os.environ.get('CONFIG_GENESIS')))
        self.echo_debug("CONFIG_CHAIN_ID={}".format(os.environ.get('CONFIG_CHAIN_ID')))
        self.echo_debug("CONFIG_DEBUG_PATH={}".format(os.environ.get('CONFIG_DEBUG_PATH')))
        
    def __init__(self):
        self.print_environment()
        if not os.environ.get('CONFIG_DEBUG_PATH'):
            self.BIN_PATH = "/usr/local/bin"
            self.SETUP_PATH = "/etc/room"
            self.CONFIG_PATH = "/var/lib/room"
        else:
            PWD = p.dirname(p.realpath(__file__))
            self.BIN_PATH = p.abspath(p.join(PWD, "..", "_build"))
            self.SETUP_PATH = p.abspath(PWD)
            self.CONFIG_PATH = p.abspath(p.join(PWD, "..","_config"))
            self.echo_debug("PWD={}".format(PWD))
            self.echo_debug("BIN_PATH={}".format(self.BIN_PATH))
            self.echo_debug("SETUP_PATH={}".format(self.SETUP_PATH))
            self.echo_debug("CONFIG_PATH={}".format(self.CONFIG_PATH))
        self.EXTERNAL_PLAYCHAIN_DATABASE_API_URL = os.environ.get('CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL')
        self.EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL = os.environ.get('CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL')
        self.PLAYCHAIN_DATABASE_API_INTERFACE = "0.0.0.0"
        if os.environ.get('CONFIG_PLAYCHAIN_DATABASE_API_PORT'):
            self.PLAYCHAIN_DATABASE_API_PORT = os.environ.get('CONFIG_PLAYCHAIN_DATABASE_API_PORT')
        else:
            self.PLAYCHAIN_DATABASE_API_PORT = 8510
        self.PLAYCHAIN_DATABASE_P2P_INTERFACE = "0.0.0.0"
        if os.environ.get('CONFIG_PLAYCHAIN_DATABASE_P2P_PORT'):
            self.PLAYCHAIN_DATABASE_P2P_PORT = os.environ.get('CONFIG_PLAYCHAIN_DATABASE_P2P_PORT')
        else:
            self.PLAYCHAIN_DATABASE_P2P_PORT = 10310
            
        if os.environ.get('CONFIG_CHAIN_ID'):
            self.CHAIN_ID = os.environ.get('CONFIG_CHAIN_ID')
        else:
            self.CHAIN_ID = None
        
        self.playchain_rpc_pid = None
        atexit.register(self.cleanup)

    def get_rpc_api_url(self):
        return "localhost:{}".format(self.PLAYCHAIN_DATABASE_API_PORT)
    
    def get_rpc_p2p_url(self):
        return "localhost:{}".format(self.PLAYCHAIN_DATABASE_P2P_PORT)
    
    def cleanup(self):
        self.echo_debug("terminated")
        if self.playchain_rpc_pid:
            os.kill(self.playchain_rpc_pid, signal.SIGTERM)
            shutil.rmtree(p.abspath(p.join(self.CONFIG_PATH, "blockchain")), ignore_errors=True)
    
    def echo_debug(self, data):
        if os.environ.get('CONFIG_DEBUG'):
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
    
    def ask_yes_or_no(self, text: str, fg = None):
        if fg:
            click_text = click.style(text, fg=fg)
        else:
            click_text = text
        return click.confirm(click_text, default=True)
        
    def abort_if_no(self, text: str, fg = None):
        if not self.ask_yes_or_no(text, fg):
            sys.exit(2)
            
    def getpass(self, text: str, fg = None):
        input_text = "{}: ".format(text)
        if fg:
            click_text = click.style(input_text, fg=fg)
        else:
            click_text = input_text     
        self.echo(click_text, nl=False)
        return getpass.getpass("")
    
    def select(self, txt: str, var: list, default_txt = None):
        return click.prompt(txt, type=click.Choice(var, case_sensitive=True),
                     show_choices=True, default=default_txt)
    
    def _post_request(self, payload: str, url: str):
        try:
            r = rpc.post("http://" + url, data=json.dumps(payload))
            if (r.status_code != 200):
                return None
        except Exception as e:
            self.echo_debug("{}".format(e))
            self.echo_error("'{}' is unreachable".format(url))
            return None
        return r.json()

    def _post_external_request(self, payload: str):
        return self._post_request(payload, self.EXTERNAL_PLAYCHAIN_DATABASE_API_URL)

    def _post_local_request(self, payload: str):
        return self._post_request(payload, self.get_rpc_api_url())
        
    # return last block number
    def get_total_blocks(self, local = False):
        payload = {"jsonrpc":"2.0","method":"call","params":["database","get_dynamic_global_properties",[]],"id":0}
        if not local:
            r = self._post_external_request(payload)
        else:
            r = self._post_local_request(payload)
        if not r or not r.get('result') or not r.get('result').get('head_block_number'):
            return None
        return r['result']['head_block_number']
    
    # return boolean type
    def get_chain_id(self, local = False):
        payload = {"jsonrpc":"2.0","method":"call","params":["database","get_chain_id",[]],"id":0}
        if not local:
            r = self._post_external_request(payload)
        else:
            r = self._post_local_request(payload)
        if not r or not r.get('result'):
            return None
        return r['result']
    
    # return boolean type
    def check_account(self, name: str, pub_key: str):
        payload = {"jsonrpc":"2.0","method":"call","params":["database","get_account_by_name",[name]],"id":0}
        r = self._post_local_request(payload)
        if not r or not r.get('result') or not r.get('result').get('active'):
            return False
        return (r['result']['active']['key_auths'][0][0] == pub_key)

    # return room_id_type
    def get_account_balance(self, name: str):
        payload = {"jsonrpc":"2.0","method":"call","params":["playchain","get_playchain_balance_info",[name]],"id":0}
        r = self._post_local_request(payload)
        if not r or not r.get('result') or not r.get('result').get('account_balance'):
            return None
        return r['result']['account_balance']['amount']
    
    def check_config(self):
        return p.exists(p.join(self.CONFIG_PATH, self.PLAYCHAIN_RUN_CONFIG_FILE_NAME))
        
    def get_genesis_file(self):
        if not os.environ.get('CONFIG_GENESIS'):
            return None
        genesis_path = p.join(self.CONFIG_PATH, self.GENESIS_FILE_NAME)
        if not p.exists(genesis_path):
            return None
        return genesis_path

    def start_payload(self):
        self.echo_progress("Starting of Playchain Witness node")
        
        args = [p.join(self.BIN_PATH, "playchaind")]
        args.append("--sticked")
        args.append("-x");
        args.append(p.join(self.CONFIG_PATH, self.PLAYCHAIN_RUN_CONFIG_FILE_NAME));
        args.append("--data-dir");
        args.append(self.CONFIG_PATH);
        genesis = self.get_genesis_file()
        if genesis:
            args.append("--genesis-json");
            args.append(genesis);
        os.execv(args[0], args)
    
    def welcome(self):
        if not os.environ.get('CONFIG_OFF_LOGO'):
            logo = """
 _    _      _                            _         ______ _                  _           _       
| |  | |    | |                          | |        | ___ \ |                | |         (_)      
| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___   | |_/ / | __ _ _   _  ___| |__   __ _ _ _ __  
| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \  |  __/| |/ _` | | | |/ __| '_ \ / _` | | '_ \ 
\  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | | |   | | (_| | |_| | (__| | | | (_| | | | | |
 \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/  \_|   |_|\__,_|\__, |\___|_| |_|\__,_|_|_| |_|
                                                                    __/ |                         
                                                                   |___/                          
        """
            for row in logo.split("\n"):
                    self.echo_ok(row)
                    time.sleep(0.05)
        self.abort_if_no("Do you want to start configurating?")
    
    def enter_external_playchain_api(self):
        if self.CHAIN_ID:
            self.echo_progress("Connecting to Playchain database API with ID:\n  {}".format(self.CHAIN_ID))
        else:
            self.echo_progress("Connecting to Playchain database API")
        base_url = self.EXTERNAL_PLAYCHAIN_DATABASE_API_URL
        while(True):
            self.EXTERNAL_PLAYCHAIN_DATABASE_API_URL = click.prompt('Please enter Playchain database API URL', 
                                                                   type=str, default=base_url)
            chain_id = self.get_chain_id()
            if not chain_id or self.CHAIN_ID and chain_id != self.CHAIN_ID:
                if chain_id and self.CHAIN_ID and chain_id != self.CHAIN_ID:
                    self.echo_warning("Different playchain ID '{}' received".format(chain_id))
                self.abort_if_no("Wrong external playchain. Do you want to set other URL?", fg='yellow')
            else:
                self.CHAIN_ID = chain_id
                break
        self.echo_ok("Playchain database '{}' API found".format(self.CHAIN_ID))
        
    def check_tcp_port(self, url: str):
        pos = url.rfind(':')
        address = None
        port = None
        if pos > 0:
            address = url[:pos]
            port = url[pos + 1:]
        if not any(address) or not any(port):
            return False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((address, int(port)))
            return True
        except Exception as e:
            self.echo_debug("{}".format(e))
            return False
        finally:
            s.close()
            
    def check_domain_name(self, name: str):
        if not name or not any(name):
            return None
        try:
            socket.gethostbyname(name)
            return True
        except Exception as e:
            self.echo_debug("{}".format(e))
            return None
                
    def enter_external_playchain_p2p(self):
        base_url = self.EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL
        while(True):
            self.EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL = click.prompt('Please enter Playchain database P2P URL', type=str, 
                                                                   default=base_url)
            if not self.check_tcp_port(self.EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL):
                self.echo_error("'{}' is unreachable".format(self.EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL))
                self.abort_if_no("Wrong external playchain. Do you want to set other URL?", fg='yellow')
            else:
                break
        self.echo_ok("Playchain database P2P found")
    
    def create_setup_rpc_config(self):
        self.echo_progress("Creation of RPC config file")
        
        setup_path = p.join(self.SETUP_PATH, self.PLAYCHAIN_SETUP_FILE_NAME)
        config_path = p.join(self.CONFIG_PATH, self.PLAYCHAIN_SETUP_CONFIG_FILE_NAME)
        try:
            with open(setup_path, "r") as f:
                lines = f.readlines()
            with open(config_path, "w") as f:
                for line in lines:
                    ln = re.sub(r'\$\{INTERFACE_P2P\}', self.PLAYCHAIN_DATABASE_P2P_INTERFACE, line)
                    ln = re.sub(r'\$\{\PORT_P2P\}', str(self.PLAYCHAIN_DATABASE_P2P_PORT), ln)
                    ln = re.sub(r'\$\{INTERFACE_API\}', self.PLAYCHAIN_DATABASE_API_INTERFACE, ln)
                    ln = re.sub(r'\$\{PORT_API\}', str(self.PLAYCHAIN_DATABASE_API_PORT), ln)
                    ln = re.sub(r'\$\{PLAYCHAIN_P2P_URL\}', str(self.EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL), ln)
                    ln = re.sub(r'^witness\-id', "# witness-id", ln)
                    ln = re.sub(r'^private\-key', "# private-key", ln)
                    ln = re.sub(r'\$\{LOG_APPENDERS\}', "stderr default", ln)
                    f.write(ln)
        except Exception as e:
            self.echo_debug("{}".format(e))
            self.echo_error("Can't create setup RPC config file")
            sys.exit(1)

    def create_run_rpc_config(self):
        self.echo_progress("Creation of RPC config file")
        
        setup_path = p.join(self.SETUP_PATH, self.PLAYCHAIN_SETUP_FILE_NAME)
        config_path = p.join(self.CONFIG_PATH, self.PLAYCHAIN_RUN_CONFIG_FILE_NAME)
        try:
            with open(setup_path, "r") as f:
                lines = f.readlines()
            with open(config_path, "w") as f:
                for line in lines:
                    ln = re.sub(r'\$\{INTERFACE_P2P\}', self.PLAYCHAIN_DATABASE_P2P_INTERFACE, line)
                    ln = re.sub(r'\$\{\PORT_P2P\}', str(self.PLAYCHAIN_DATABASE_P2P_PORT), ln)
                    ln = re.sub(r'\$\{INTERFACE_API\}', self.PLAYCHAIN_DATABASE_API_INTERFACE, ln)
                    ln = re.sub(r'\$\{PORT_API\}', str(self.PLAYCHAIN_DATABASE_API_PORT), ln)
                    ln = re.sub(r'\$\{PLAYCHAIN_P2P_URL\}', str(self.EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL), ln)
                    ln = re.sub(r'\$\{WITNESS_ID\}', str(self.WITNESS_ID), ln)
                    ln = re.sub(r'\$\{WITNESS_SIGN_PUBKEY\}', str(self.WITNESS_SIGN_PUBKEY), ln)
                    ln = re.sub(r'\$\{WITNESS_SIGN_PRVKEY\}', str(self.WITNESS_SIGN_PRVKEY), ln)
                    ln = re.sub(r'\$\{LOG_APPENDERS\}', "default", ln)
                    f.write(ln)
        except Exception as e:
            self.echo_debug("{}".format(e))
            self.echo_error("Can't create runnable RPC config file")
            sys.exit(1)
            
    def synchronize_rpc(self):
        self.create_setup_rpc_config()
        
        self.echo_progress("Starting Playchain database synchronization")
        
        args = [p.join(self.BIN_PATH, "playchaind")]
        args.append("-x");
        args.append(p.join(self.CONFIG_PATH, self.PLAYCHAIN_SETUP_CONFIG_FILE_NAME));
        args.append("--data-dir");
        args.append(self.CONFIG_PATH);
        genesis = self.get_genesis_file()
        if genesis:
            args.append("--genesis-json");
            args.append(genesis);
    
        total_blocks=self.get_total_blocks()
        
        self.echo_debug("Waiting synchronization till block {}".format(total_blocks))
        self.echo_ok("Synchronization of Playchain database")
        with click.progressbar(length=total_blocks, width=self.PROGRESSBAR_BAR_WIDTH,
                           label=self.PROGRESSBAR_TEXT) as bar:
            bar.pos = 0
            bar.update(0)
            time.sleep(1.2)
            self.echo_debug("Run {}".format(args))
            playchain_rpc_proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
            self.playchain_rpc_pid = playchain_rpc_proc.pid
            self.echo_debug("Started subprocess {} pid = {}".format(args[0], self.playchain_rpc_pid))
            while True:
                bar.update(0)
                ln = str(playchain_rpc_proc.stderr.readline(), 'utf-8').rstrip()
                if ln.find("Sync block") >= 0:
                    b = int(re.search('\s+#(\d+?)\s+', ln).group(1))
                    if b  > 0 and b  < total_blocks: 
                        bar.pos = b
                        bar.update(0)
                if ln.find("Got block") >= 0:
                    break
                if not any(ln):
                    break
                
            bar.pos = total_blocks
            bar.update(0)             
        
        if total_blocks <= self.get_total_blocks(True):
            self.echo_ok("Playchain database synchronization completed")
        else:
            self.echo_error("Synchronization failed")
            sys.exit(1)
    
    def get_private_key(self, name: str, psw: str = None, wif: str = None):
        args = [p.join(self.BIN_PATH, "keys_from_login")]
        args.append("-n");
        args.append(name);
        if psw:
            args.append("-s");
            args.append(psw);
        if wif:
            args.append("-w");
            args.append(wif);
        args.append("--print-private");
        args.append("true");
        args.append("--print-public-raw");
        args.append("false");
        args.append("--print-public");
        args.append("true");
        self.echo_debug("Run {}".format(args))
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        self.echo_debug("Started subprocess {} pid = {}".format(args[0], proc.pid))
        for ln in proc.stdout.readlines():
            ln = str(ln, 'utf-8').rstrip()
            if ln.startswith("PLC"):
                pub_key=ln
            else:
                priv_key=ln
        return (pub_key, priv_key)
    
    def get_login_data_from_config(self):
        # TODO
        
        return (None, None)
    
    def login(self):
        self.echo_progress("Login")
        (name, wif_key) = self.get_login_data_from_config()
        while(not name or not wif_key):
            if name:
                name = click.prompt('Enter room owner name', type=str, show_default=True, default=name)
            else:
                name = click.prompt('Enter room owner name', type=str)
            
            if (not wif_key):
                psw = self.getpass('Enter room owner password')
                (pub_key, wif_key) = self.get_private_key(name, psw = psw)
            else:
                (pub_key, wif_key) = self.get_private_key(name, wif = wif_key)
            
            if self.check_account(name, pub_key):
                break
            else:
                name = None
                wif_key = None
                self.abort_if_no("Wrong credentials. Make sure that such user exists. Try again?", fg='yellow')
        
        self.OWNER_NAME = name
        self.OWNER_WIF = wif_key
        self.echo_ok("Hellow '{}', let's configure you Playchain Witness".format(self.OWNER_NAME))
    
    def config_witness(self):
        
        # TODO: create_run_rpc_config
        raise Exception("Not implemented")
    
    def close_temp_rpc(self):
        self.echo_debug("Close temp RPC {}".format(self.playchain_rpc_pid))
        if self.playchain_rpc_pid:
            os.kill(self.playchain_rpc_pid, signal.SIGTERM)
            while True:
                self.echo_debug("Wait temp RPC closing")
                time.sleep(3)
                if not self.check_tcp_port(self.get_rpc_p2p_url()) and \
                   not self.check_tcp_port(self.get_rpc_api_url()):
                    break
            time.sleep(5)
            self.playchain_rpc_pid = None
    
    def syslog_test(self):
        import syslog
        syslog.syslog("Check write access")
    
app = APP()

def main():
    app.echo_progress("* *")
    app.syslog_test()
    if os.environ.get('CONFIGURATE'):
        app.welcome()
        app.enter_external_playchain_api()
        app.enter_external_playchain_p2p()
        app.synchronize_rpc()
        app.login()
        app.config_witness()
        app.close_temp_rpc()
        app.echo_ok("Configuration is completed. Need restart to leave interactive mode")
    else:
        if not app.check_config():
            self.echo_error("Playchain witness node is not configured.\n" +
                            "Reload node to interactive mode and setup")
            sys.exit(1)        
        app.start_payload()
    sys.exit(0)
    
if __name__ == '__main__':
    main()

