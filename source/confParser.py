'''
##############################################################################
# Copyright 2021 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

Created on Feb 15, 2021

@author: HWASSMAN
'''

import argparse
import os
import logging.handlers
from messages import MSG
import configparser


def checkFileExists(path, filename):
    for root, dirs, files in os.walk(path):
        if filename in files:
            return True
    return False


def checkTLSsettings(args):
    if args.get('port') == 8443 and (not args.get('tlsKeyPath') or not args.get('tlsKeyFile') or not args.get('tlsCertFile')):
        return False, MSG['MissingParm']
    elif args.get('port') == 8443 and not os.path.exists(args.get('tlsKeyPath')):
        return False, MSG['KeyPathError']
    elif args.get('port') == 8443:
        if (not checkFileExists(args.get('tlsKeyPath'), args.get('tlsCertFile'))) or (not checkFileExists(args.get('tlsKeyPath'), args.get('tlsKeyFile'))):
            return False, MSG['CertError']
    return True, ''


def getSettings(argv):
    settings = {}
    msg = ''
    args, msg = parse_cmd_args(argv)
    defaults = parse_defaults_from_config_file()
    if args and defaults:
        settings = merge_defaults_and_args(defaults, args)
    elif args:
        settings = args
    else:
        return None, msg
    # check TLS settings
    valid, msg = checkTLSsettings(settings)
    if valid:
        return settings, ''
    return None, msg


def merge_defaults_and_args(defaults, args):
    '''merge default config parameters with input parameters from the command line'''
    brConfig = {}
    brConfig = dict(defaults)
    args = vars(args)
    brConfig.update({k: v for k, v in args.items() if v is not None})
    return brConfig


def parse_defaults_from_config_file(fileName='config.ini'):
    '''parse default parameters from a config file'''
    defaults = {}
    dirname, filename = os.path.split(os.path.abspath(__file__))
    conf_file = os.path.join(dirname, fileName)
    if os.path.isfile(conf_file):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(conf_file)
        for sect in config.sections():
            for name, value in config.items(sect):
                defaults[name] = value
    return defaults


def parse_cmd_args(argv):
    '''parse input parameters'''

    parser = argparse.ArgumentParser('python zimonGrafanaIntf.py')
    parser.add_argument('-s', '--server', action="store", default='localhost',
                        help='Host name or ip address of the ZIMon collector (Default: 127.0.0.1) \
                        NOTE: Per default ZIMon does not accept queries from remote machines. \
                        To run the bridge from outside of the ZIMon collector, you need to modify ZIMon queryinterface settings (\'ZIMonCollector.cfg\')')
    parser.add_argument('-P', '--serverPort', action="store", type=int, default=9084, help='ZIMon collector port number (Default: 9084)')
    parser.add_argument('-l', '--logPath', action="store", default="/var/log/ibm_bridge_for_grafana", help='location path of the log file (Default: /var/log/ibm_bridge_for_grafana')
    parser.add_argument('-f', '--logFile', action="store", default="zserver.log", help='Name of the log file (Default: zserver.log')
    parser.add_argument('-c', '--logLevel', action="store", type=int, default=logging.INFO, help='log level 10 (DEBUG), 20 (INFO), 30 (WARN), 40 (ERROR) (Default: 20)')
    parser.add_argument('-p', '--port', action="store", type=int, choices=[4242, 8443], default=4242, help='port number listening on for HTTP(S) connections (Default: 4242)')
    parser.add_argument('-t', '--tlsKeyPath', action="store", default=None, help='Directory path of tls privkey.pem and cert.pem file location (Required only for HTTPS port 8443)')
    parser.add_argument('-k', '--tlsKeyFile', action="store", default=None, help='Name of TLS key file, f.e.: privkey.pem (Required only for HTTPS port 8443)')
    parser.add_argument('-m', '--tlsCertFile', action="store", default=None, help='Name of TLS certificate file, f.e.: cert.pem (Required only for HTTPS port 8443)')

    args = parser.parse_args(argv)
    return args, ''