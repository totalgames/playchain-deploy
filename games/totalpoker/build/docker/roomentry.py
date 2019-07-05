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
    PLAYCHAIN_SETUP_CONFIG_FILE_NAME = "playchain.setup.config.ini"
    PLAYCHAIN_RUN_CONFIG_FILE_NAME = "playchain.config.ini"
    POKER_ROOM_CONFIG_FILE_NAME = "poker_room.config.ini"
    PLAYCHAIN_SETUP_FILE_NAME = "playchain.config.template.ini"
    POKER_ROOM_SETUP_FILE_NAME = "poker_room.config.template.ini"
    POKER_ROOM_TABLES_INFO_FILE_NAME = "tables.info"
    PLAYCHAIN_TLS_SERVER_PEM = "certificate.pem"
    GENESIS_FILE_NAME = "genesis.json"
    PAGE_SIZE = 5
    NEW_ROOM = "new"
    NEXT_ROOM = "next"
    DEFAULT_ROOM = "default"
    PROGRESSBAR_TEXT = "Waiting:"
    PROGRESSBAR_BAR_WIDTH = 51
    
    def print_environment(self):
        self.echo_debug("* ROOMENTRY.PY")
        self.echo_debug("CONFIGURATE={}".format(os.environ.get('CONFIGURATE')))
        self.echo_debug("CONFIG_OFF_LOGO={}".format(os.environ.get('CONFIG_OFF_LOGO')))
        self.echo_debug("CONFIG_DEBUG={}".format(os.environ.get('CONFIG_DEBUG')))
        self.echo_debug("CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL={}".format(os.environ.get('CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_API_URL')))
        self.echo_debug("CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL={}".format(os.environ.get('CONFIG_EXTERNAL_PLAYCHAIN_DATABASE_P2P_URL')))
        self.echo_debug("CONFIG_PLAYCHAIN_DATABASE_API_PORT={}".format(os.environ.get('CONFIG_PLAYCHAIN_DATABASE_API_PORT')))
        self.echo_debug("CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT={}".format(os.environ.get('CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT')))
        self.echo_debug("CONFIG_PLAYCHAIN_DATABASE_P2P_PORT={}".format(os.environ.get('CONFIG_PLAYCHAIN_DATABASE_P2P_PORT')))
        self.echo_debug("CONFIG_POKER_ROOM_PORT={}".format(os.environ.get('CONFIG_POKER_ROOM_PORT')))
        self.echo_debug("CONFIG_POKER_ROOM_CONTROL_PORT={}".format(os.environ.get('CONFIG_POKER_ROOM_CONTROL_PORT')))
        self.echo_debug("CONFIG_GENESIS={}".format(os.environ.get('CONFIG_GENESIS')))
        self.echo_debug("CONFIG_CHAIN_ID={}".format(os.environ.get('CONFIG_CHAIN_ID')))
        self.echo_debug("CONFIG_DEBUG_PATH={}".format(os.environ.get('CONFIG_DEBUG_PATH')))
        self.echo_debug("CONFIG_TEST_TAG={}".format(os.environ.get('CONFIG_TEST_TAG')))
        
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
            self.PLAYCHAIN_DATABASE_API_PORT = 8500
        self.PLAYCHAIN_DATABASE_TLS_API_INTERFACE = "0.0.0.0"
        if os.environ.get('CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT'):
            self.PLAYCHAIN_DATABASE_TLS_API_PORT = os.environ.get('CONFIG_PLAYCHAIN_DATABASE_TLS_API_PORT')
        else:
            self.PLAYCHAIN_DATABASE_TLS_API_PORT = 8501
        self.PLAYCHAIN_DATABASE_P2P_INTERFACE = "0.0.0.0"
        if os.environ.get('CONFIG_PLAYCHAIN_DATABASE_P2P_PORT'):
            self.PLAYCHAIN_DATABASE_P2P_PORT = os.environ.get('CONFIG_PLAYCHAIN_DATABASE_P2P_PORT')
        else:
            self.PLAYCHAIN_DATABASE_P2P_PORT = 10300
        self.POKER_ROOM_INTERFACE = "0.0.0.0"
        if os.environ.get('CONFIG_POKER_ROOM_PORT'):
            self.POKER_ROOM_PORT = os.environ.get('CONFIG_POKER_ROOM_PORT')
        else:
            self.POKER_ROOM_PORT = 8092
            
        # TODO: remove POKER_ROOM_CONTROL_PORT
        if os.environ.get('CONFIG_POKER_ROOM_CONTROL_PORT'):
            self.POKER_ROOM_CONTROL_PORT = os.environ.get('CONFIG_POKER_ROOM_CONTROL_PORT')
        else:
            self.POKER_ROOM_CONTROL_PORT = 9100
        
        if os.environ.get('CONFIG_TEST_TAG'):
            self.TEST_TAG = os.environ.get('CONFIG_TEST_TAG')
        else:
            self.TEST_TAG = ""
            
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
    
    def get_bool_environ(self, env_name: str):
        r = os.environ.get(env_name)
        if not r or r == 'False':
            return False
        return True
        
    def echo_debug(self, data):
        if self.get_bool_environ('CONFIG_DEBUG'):
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
            self.echo_debug("POST to '{}' Data: {}".format(url, json.dumps(payload)))
            r = rpc.post("http://" + url, data=json.dumps(payload))
            if (r.status_code != 200):
                self.echo_debug("Result = Code '{}'".format(r.status_code))
                return None
            self.echo_debug("Result = '{}'".format(r.json()))
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
    
    # return room (id, name) list
    def list_all_rooms(self, owner_name: str, from_room: str = ""):
        payload = {"jsonrpc":"2.0","method":"call","params":["playchain","list_rooms",[owner_name, from_room, self.PAGE_SIZE]],"id":0}
        r = self._post_local_request(payload)
        if not r or not r.get('result'):
            return None
        result = []
        for item in r['result']:
            result.append((item['id'], item['metadata']));
        return result
    
    # return room_id_type
    def get_room_by_name(self, owner_name: str, room_name: str = ""):
        payload = {"jsonrpc":"2.0","method":"call","params":["playchain","get_room_info",[owner_name, room_name]],"id":0}
        r = self._post_local_request(payload)
        if not r or not r.get('result') or not r.get('result').get('id'):
            return None
        return r.get('result')
    
    # return room_id_type
    def get_account_balance(self, name: str):
        payload = {"jsonrpc":"2.0","method":"call","params":["playchain","get_playchain_balance_info",[name]],"id":0}
        r = self._post_local_request(payload)
        if not r or not r.get('result') or not r.get('result').get('account_balance'):
            return None
        return r['result']['account_balance']['amount']
    
    def check_config(self):
        return p.exists(p.join(self.CONFIG_PATH, self.PLAYCHAIN_RUN_CONFIG_FILE_NAME)) and \
               p.exists(p.join(self.CONFIG_PATH, self.POKER_ROOM_CONFIG_FILE_NAME))
    
    def check_tls_config(self):
        if any(self.PLAYCHAIN_DATABASE_TLS_API_INTERFACE) and \
           self.PLAYCHAIN_DATABASE_TLS_API_PORT in range(1024, 49151):
            return p.exists(p.join(self.CONFIG_PATH, self.PLAYCHAIN_TLS_SERVER_PEM))
        return None
    
    def get_genesis_file(self):
        if not os.environ.get('CONFIG_GENESIS'):
            return None
        genesis_path = p.join(self.CONFIG_PATH, self.GENESIS_FILE_NAME)
        if not p.exists(genesis_path):
            return None
        return genesis_path

    def restart_rpc(self):
        self.echo_progress("Restarting of Playchain RPC")
        total_blocks = self.get_total_blocks()
        pid = os.fork()
        if pid == 0:
            args = [p.join(self.BIN_PATH, "playchaind")]
            args.append("-x");
            args.append(p.join(self.CONFIG_PATH, self.PLAYCHAIN_SETUP_CONFIG_FILE_NAME));
            args.append("--data-dir");
            args.append(self.CONFIG_PATH);
            genesis = self.get_genesis_file()
            if genesis:
                args.append("--genesis-json");
                args.append(genesis);
            os.execv(args[0], args)
        
        self.playchain_rpc_pid = pid
        self.echo_progress("Waiting RPC launch")
        while True:
            time.sleep(3)
            if self.get_chain_id(True):
                break
                
    def start_payload(self):
        self.echo_progress("Starting of Playchain Poker Room couple")
        total_blocks = self.get_total_blocks()
        pid = os.fork()
        if pid == 0:
            args = [p.join(self.BIN_PATH, "playchaind")]
            args.append("--sticked")
            args.append("-x");
            args.append(p.join(self.CONFIG_PATH, self.PLAYCHAIN_RUN_CONFIG_FILE_NAME));
            args.append("--data-dir");
            args.append(self.CONFIG_PATH);
            if self.check_tls_config():
                args.append("--rpc-tls-endpoint");
                args.append("{}:{}".format(self.PLAYCHAIN_DATABASE_TLS_API_INTERFACE, self.PLAYCHAIN_DATABASE_TLS_API_PORT));
                args.append("--server-pem");
                args.append(p.join(self.CONFIG_PATH, self.PLAYCHAIN_TLS_SERVER_PEM));
            genesis = self.get_genesis_file()
            if genesis:
                args.append("--genesis-json");
                args.append(genesis);
            os.execv(args[0], args)
    
        self.playchain_rpc_pid = pid
        self.echo_progress("Waiting RPC launch")
        while True:
            time.sleep(3)
            if self.get_chain_id(True):
                break
        
        # a little bit time to synchronize tail of chain
        time.sleep(15)

        if total_blocks <= self.get_total_blocks(True):
            self.echo_ok("Playchain database synchronized")
        else:
            self.echo_error("Need in synchronization. Restart in config-mode to synchronization RPC")
            sys.exit(1)

        self.playchain_rpc_pid = None
        args = [p.join(self.BIN_PATH, "poker_room")]
        args.append("-x");
        args.append(p.join(self.CONFIG_PATH, self.POKER_ROOM_CONFIG_FILE_NAME));
        os.execv(args[0], args)
    
    def welcome(self):
        if not self.get_bool_environ('CONFIG_OFF_LOGO'):
            logo = """
 _    _      _                            _         ______ _                  _           _       
| |  | |    | |                          | |        | ___ \ |                | |         (_)      
| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___   | |_/ / | __ _ _   _  ___| |__   __ _ _ _ __  
| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \  |  __/| |/ _` | | | |/ __| '_ \ / _` | | '_ \ 
\  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | | |   | | (_| | |_| | (__| | | | (_| | | | | |
 \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/  \_|   |_|\__,_|\__, |\___|_| |_|\__,_|_|_| |_|
                                                                    __/ |                         
                                                                   |___/                          
 _____     _        _  ______     _                ___ ___ ___ ___ ___ ___ ___ ___ ___ ___        
|_   _|   | |      | | | ___ \   | |              |  _|_  |  _|_  |  _|_  |  _|_  |  _|_  |       
  | | ___ | |_ __ _| | | |_/ /__ | | _____ _ __   | |   | | |   | | |   | | |   | | |   | |       
  | |/ _ \| __/ _` | | |  __/ _ \| |/ / _ \ '__|  | |   | | |   | | |   | | |   | | |   | |       
  | | (_) | || (_| | | | | | (_) |   <  __/ |     | |   | | |   | | |   | | |   | | |   | |       
  \_/\___/ \__\__,_|_| \_|  \___/|_|\_\___|_|     | |_ _| | |_ _| | |_ _| | |_ _| | |_ _| |       
                                                  |___|___|___|___|___|___|___|___|___|___|       
                                                                                                  
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
    
    def create_rpc_config(self):
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
                    ln = re.sub(r'\$\{LOG_APPENDERS\}', "stderr default", ln)
                    f.write(ln)
        except Exception as e:
            self.echo_debug("{}".format(e))
            self.echo_error("Can't create setup RPC config file")
            sys.exit(1)
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
                    ln = re.sub(r'\$\{LOG_APPENDERS\}', "default", ln)
                    f.write(ln)
        except Exception as e:
            self.echo_debug("{}".format(e))
            self.echo_error("Can't create runnable RPC config file")
            sys.exit(1)
        
    def synchronize_rpc(self):
        self.create_rpc_config()
        
        self.echo_progress("Starting Playchain database synchronization")
        
        args = [p.join(self.BIN_PATH, "playchaind")]
        args.append("-x")
        args.append(p.join(self.CONFIG_PATH, self.PLAYCHAIN_SETUP_CONFIG_FILE_NAME));
        args.append("--data-dir");
        args.append(self.CONFIG_PATH);
        genesis = self.get_genesis_file()
        if genesis:
            args.append("--genesis-json");
            args.append(genesis);
    
        synch_blocks = 0
        total_blocks = self.get_total_blocks()
        
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
            while synch_blocks < total_blocks:
                bar.update(0)
                time.sleep(3)
                synch_blocks = self.get_total_blocks(True)
                if not synch_blocks:
                    synch_blocks = 0
                if synch_blocks  > 0 and synch_blocks < total_blocks: 
                    bar.pos = synch_blocks
                    bar.update(0)
                
            bar.pos = total_blocks
            bar.update(0)
        
        self.close_temp_rpc();
            
        total_blocks = self.get_total_blocks()
        
        if total_blocks > synch_blocks:
            self.echo_ok("Finalizing synchronization for {} blocks".format(total_blocks - synch_blocks))
        
        self.restart_rpc()
        
        while synch_blocks < total_blocks:
            time.sleep(6)
            synch_blocks = self.get_total_blocks(True)

        self.echo_ok("Playchain database synchronization completed")
    
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
        ini_path = p.join(self.CONFIG_PATH, self.POKER_ROOM_CONFIG_FILE_NAME)
        if not p.exists(ini_path):
            return (None, None)
        name = None
        wif_key = None
        with open(ini_path) as f:
            for line in f:
                ln_n = re.search('^owner = (\w+?)$', line)
                if ln_n:
                    name = str(ln_n.group(1))
                else:
                    ln_p = re.search('^owner\-key = (\w+?)$', line)
                    if ln_p:
                        wif_key = str(ln_p.group(1))
                if name and wif_key:
                    break
        return (name, wif_key)
    
    def login(self):
        self.echo_progress("Login")
        (name, wif_key) = self.get_login_data_from_config()
        if name and wif_key:
            (pub_key, wif_key) = self.get_private_key(name, wif = wif_key)
            if not self.check_account(name, pub_key):
                (name, wif_key) = (None, None)
                
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
        self.echo_ok("Hellow '{}', let's configure you Playchain Poker Room".format(self.OWNER_NAME))
        
    def choose_or_create_room(self):
        self.ROOM_NAME = self.NEW_ROOM
        self.echo_debug("ROOM_NAME {}".format(self.ROOM_NAME))
        from_room = ""
        next_rooms = self.list_all_rooms(self.OWNER_NAME, from_room)
        while(next_rooms and any(next_rooms)):
            rooms = next_rooms
            self.echo_debug(rooms)
            
            room_names = []
            default_room = None
            for r in rooms:
                (from_room, n) = r
                if not any(n):
                    default_room = self.DEFAULT_ROOM
                else:
                    room_names.append(n)
                    
            next_rooms = self.list_all_rooms(self.OWNER_NAME, from_room)
            if default_room != None:
                room_names.insert(0, default_room)
            room_names.append(self.NEW_ROOM)
            if next_rooms and any(next_rooms):
                room_names.append(self.NEXT_ROOM)
                
            self.ROOM_NAME = self.select("Select room to configurate", room_names, default_room)
                    
            if self.ROOM_NAME != self.NEXT_ROOM:
                break
            
        if self.ROOM_NAME == self.NEW_ROOM:
            self.abort_if_no("Create new room?")
            self.create_new_room()
        else:
            room = self.get_room_by_name(self.OWNER_NAME, self.ROOM_NAME)
            if not room:
                self.echo_error("Can't get room info")
                sys.exit(1)                
            self.POKER_ROOM_URL = room["server_url"]
            if (not self.ask_yes_or_no("Keep current address '{}' unchanged?".format(self.POKER_ROOM_URL))):
                self.config_room_url()
            self.config_seleted_room(False)
    
    def config_room_url(self):
        while(True):
            while(True):
                poker_room_address = click.prompt('Enter server domain name on which you will serve your players', 
                                                   type=str)  
                if not self.check_domain_name(poker_room_address):
                    self.echo_error("'{}' is unreachable".format(poker_room_address))
                    self.abort_if_no("Wrong domain name. Do you want to set other one?", fg='yellow')
                else:
                    break
            
            self.echo_ok("You domain name is successfully resolved")
            
            poker_room_port = click.prompt('Enter the port for URL. {}'.format(
                            click.style('Make sure the firewall settings are correct', fg='red')), 
                                                type=click.IntRange(1024, 49151), default=self.POKER_ROOM_PORT)  
            
            self.POKER_ROOM_URL = "{}:{}".format(poker_room_address,  poker_room_port)
            
            if self.ask_yes_or_no("Your players will be served at URL '{}'.\n".format(self.POKER_ROOM_URL) + 
                                  "Are you sure that this address will be available on the Internet"):
                break
        
    def create_new_room(self):
        self.echo_progress("Creation of new poker room")
        
        while(True):
            self.ROOM_NAME = click.prompt('Enter new room name', type=str).strip()
            if self.ROOM_NAME in [self.DEFAULT_ROOM, self.NEW_ROOM, self.NEXT_ROOM] or \
               self.get_room_by_name(self.OWNER_NAME, self.ROOM_NAME):
                self.abort_if_no("Wrong room name. Do you want to enter other one?", fg='yellow')
            else:
                break
        
        self.config_room_url()
        self.config_seleted_room(True)
    
    def get_poker_room_tables_info(self):
        config_path = p.join(self.CONFIG_PATH, self.POKER_ROOM_TABLES_INFO_FILE_NAME)
        if not p.exists(config_path):
            self.echo_error("Can't find poker room tables info file")
            sys.exit(1)
        return config_path
    
    def get_table_ids_list(self, conf_ids: list):
        ret = []
        for ln in conf_ids:
            ret.append(ln.split('"')[1])
        return ret
        
    def config_seleted_room(self, new_room: bool):
        if new_room:
            TXT_VERB = "create"
            TXT_VERB_P = "created"
            TXT_NOUN = "Creation"
            TXT_QUES = "Create?"
        else:
            TXT_VERB = "change"
            TXT_VERB_P = "changed"
            TXT_NOUN = "Changing"
            TXT_QUES = "Change?"
            
        config_path = self.get_poker_room_tables_info()
        
        args = [p.join(self.BIN_PATH, "create_service_list")]
        args.append("--owner");
        args.append(self.OWNER_NAME);
        args.append("--owner-key");
        args.append(self.OWNER_WIF);
        args.append("--room-server-url");
        args.append(self.POKER_ROOM_URL);
        args.append("--room-name");
        args.append(self.ROOM_NAME);
        args.append("--test-tag");
        args.append(self.TEST_TAG);
        args.append("--playchain-url");
        args.append("ws://{}".format(self.get_rpc_api_url()));
        args.append("--playchain-id");
        args.append(self.CHAIN_ID);
        args.append("-x");
        args.append(config_path);
        
        base_args =  copy.deepcopy(args)
        
        args.append("-f");
        self.echo_debug("Run {}".format(args))
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.echo_debug("Started subprocess {} pid = {}".format(args[0], proc.pid))
        cost = None
        for ln in proc.stdout.readlines():
            ln = str(ln, 'utf-8').rstrip()
            self.echo_debug(ln)
            if ln.endswith("PLC"):
                cost = ln
                break
        
        if not cost:
            self.echo_error("Can't estimate room {}".format(TXT_NOUN.lower()))
            sys.exit(1)
        
        balance = self.get_account_balance(self.OWNER_NAME)
        self.echo_debug("balance '{}'".format(balance))
        if balance:
            balance = int(balance) / 100000.0
        cost_balance = float(re.search('^(\d+\.?\d+|\d+)\s+PLC', ln).group(1))
            
        if cost_balance > balance:
            self.echo_error("Insufficient funds to {} room.\n".format(TXT_VERB) +
                            "Balance {0:.2f} PLC, but required {1}".format(round(balance,2), cost_balance))
            sys.exit(1)
        
        if (cost_balance > 0):
            self.abort_if_no("{} of new poker room '{}' costs {}. {}".format(TXT_NOUN, self.ROOM_NAME, cost, TXT_QUES))
        
        self.PLAYCHAIN_TABLES = []
        args = base_args
        if (cost_balance > 0):
            pr_label = 'Poker room {}'.format(TXT_NOUN.lower())
        else:
            pr_label = 'Poker room loading'
        self.echo_ok(pr_label)
        with click.progressbar(length=self.PROGRESSBAR_BAR_WIDTH, width=self.PROGRESSBAR_BAR_WIDTH,
                           label=self.PROGRESSBAR_TEXT) as bar:
            bar.pos = 0
            bar.update(0)
            time.sleep(1.2)
            self.echo_debug("Run {}".format(args))
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.echo_debug("Started subprocess {} pid = {}".format(args[0], proc.pid))
            while True:
                ln_stderr = str(proc.stderr.readline(), 'utf-8').rstrip()
                if any(ln_stderr):
                    #self.echo_debug(ln_stderr)
                    ln_r = re.search('^progress length = (\d+?)$', ln_stderr)
                    if ln_r:
                        bar.length = int(ln_r.group(1))
                        if bar.length < 1:
                            break
                    else:
                        ln_r = re.search('^progress pos = (\d+?)$', ln_stderr)
                        if ln_r:
                            bar_pos = int(ln_r.group(1))
                            if bar_pos  > 0 and bar_pos  < bar.length: 
                                bar.pos = bar_pos
                                bar.update(0)
                else:
                    break
            while True:
                ln_stdout = str(proc.stdout.readline(), 'utf-8').rstrip()
                if any(ln_stdout):
                    #self.echo_debug(ln_stdout)
                    if re.search('^table\-id\s+=\s+', ln_stdout):
                        self.PLAYCHAIN_TABLES.append(ln_stdout)
                else:
                    break
            bar.pos = bar.length
            bar.update(0)
        
        if any(self.PLAYCHAIN_TABLES):
            self.echo_debug("Loaded tables {}".format(self.get_table_ids_list(self.PLAYCHAIN_TABLES)))
            if cost_balance > 0:
                self.echo_ok("Playchain poker room '{}' successfully {}.".format(self.ROOM_NAME, TXT_VERB_P))
            else:
                self.echo_ok("Playchain poker room '{}' successfully loaded.".format(self.ROOM_NAME))
        else:
            self.echo_error("Can't {} poker room".format(TXT_VERB))
            sys.exit(1)
    
    def create_poker_room_config(self):
        self.echo_progress("Creation of poker room config file")
        
        setup_path = p.join(self.SETUP_PATH, self.POKER_ROOM_SETUP_FILE_NAME)
        config_path = p.join(self.CONFIG_PATH, self.POKER_ROOM_CONFIG_FILE_NAME)
        try:
            with open(setup_path, "r") as f:
                lines = f.readlines()
            with open(config_path, "w") as f:
                for line in lines:
                    ln = re.sub(r'\$\{INTERFACE\}', self.POKER_ROOM_INTERFACE, line)
                    ln = re.sub(r'\$\{PORT_MAIN\}', str(self.POKER_ROOM_PORT), ln)
                    ln = re.sub(r'\$\{PORT_CONROL\}', str(self.POKER_ROOM_CONTROL_PORT), ln)
                    ln = re.sub(r'\$\{PLAYCHAIN_URL\}', "ws://{}".format(self.get_rpc_api_url()), ln)
                    ln = re.sub(r'\$\{PLAYCHAIN_ID\}', self.CHAIN_ID, ln)
                    ln = re.sub(r'\$\{OWNER\}', self.OWNER_NAME, ln)
                    ln = re.sub(r'\$\{OWNER_KEY\}', self.OWNER_WIF, ln)
                    f.write(ln)
                f.write('\n')
                for ln in self.PLAYCHAIN_TABLES:
                    f.write("{}\n".format(ln))
        except Exception as e:
            self.echo_debug("{}".format(e))
            self.echo_error("Can't create poker room config file")
            sys.exit(1)
            
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
        app.choose_or_create_room()
        app.create_poker_room_config()
        app.close_temp_rpc()
        app.echo_ok("Configuration is completed. Need restart to leave interactive mode")
    else:
        if not app.check_config():
            self.echo_error("Playchain poker node is not configured.\n" +
                            "Reload node to interactive mode and setup")
            sys.exit(1)        
        app.start_payload()
    sys.exit(0)
    
if __name__ == '__main__':
    main()

