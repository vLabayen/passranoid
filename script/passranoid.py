#!/usr/bin/python3
import sys
import os
import argparse
from pmanager import PasswdManager
from getpass import getpass
from easycolor import ecprint

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog = '{}'.format(
    'examples'
))
parser.add_argument('db', help = argparse.SUPPRESS)
parser.add_argument('privkey', help = argparse.SUPPRESS)
parser.add_argument('pubkey', help = argparse.SUPPRESS)
parser.add_argument('command', metavar = 'command', choices = ['create', 'select', 'insert', 'list', 'generate', 'session'], help = 'command to execute. Available options are:\n\t{}'.format('\n\t'.join([
    '- create : create a new database',
    '- select : select a password by a service',
    '- insert : insert a password for a service',
    '- list : list all passwords and services',
    '- generate : generate a new password',
    '- session : open an interactive session'
])))
parser.add_argument('args', help = argparse.SUPPRESS, nargs = '*')
# Not refresh db
# alphabet and length for generate
parser.add_argument('-v', '--verbose', help = 'show info and progress', action = 'store_true', default = False)
args = parser.parse_args()

def create(passwd = None, passphrase = None, dbfile = None):
    db = dbfile if dbfile is not None else args.db
    if os.path.isfile(db):
        ecprint(db, c = 'yellow', template = 'Database {} already exists!')
        ecprint('[y/n]', c = 'yellow', template = 'Do you want to override it? {}: ', end="")
        r = input()
        while r != 'n' and r != 'y':
            ecprint('[y/n]', c = 'yellow', template = 'Do you want to override it? {}: ', end="")
            r = input()
        if r == 'n' : return

    if passwd is None:
        passwd = getpass('Password: ')
        rpasswd = getpass('Enter same password again: ')
        if passwd != rpasswd :
            ecprint('Passwords do not match', c = 'red')
            return

    if os.path.isfile(args.privkey) and os.path.isfile(args.pubkey):
        if args.verbose : ecprint('Using existing rsa key pair', c = 'blue')
        passphrase = "" 	   #Not used in create
        createRSA = False
    else:
        if passphrase is None:
            passphrase = getpass('Passphrase (Empty for no passphrase): ')
            rpassphrase = getpass('Enter same passphrase again: ')
            if passphrase is not rpassphrase :
                ecprint('Passphrases do not match', c = 'red')
                return
        createRSA = True

    PasswdManager(db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).create(createRSA)
def select(passwd = None, passphrase = None, service = None):
    if not os.path.isfile(args.db): ecprint(['database not found', args.db], c = ['red','yellow'], template = '{} {}')
    if not os.path.isfile(args.privkey): ecprint(['privkey not found', args.privkey], c = ['red','yellow'], template = '{} {}')
    if not os.path.isfile(args.pubkey): ecprint(['pubkey not found', args.pubkey], c = ['red','yellow'], template = '{} {}')
    if (not os.path.isfile(args.db)) or (not os.path.isfile(args.privkey)) or (not os.path.isfile(args.pubkey)): return

    if passwd is None: passwd = getpass('Password: ')
    if passphrase is None: passphrase = getpass('Passphrase (Empty if no passphrase): ')
    if service is None: service = input('Service: ')

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).select(service)
def insert(passwd = None, passphrase = None, service = None, spass = None):
    if not os.path.isfile(args.db): ecprint(['database not found', args.db], c = ['red','yellow'], template = '{} {}')
    if not os.path.isfile(args.privkey): ecprint(['privkey not found', args.privkey], c = ['red','yellow'], template = '{} {}')
    if not os.path.isfile(args.pubkey): ecprint(['pubkey not found', args.pubkey], c = ['red','yellow'], template = '{} {}')
    if (not os.path.isfile(args.db)) or (not os.path.isfile(args.privkey)) or (not os.path.isfile(args.pubkey)): return

    if passwd is None : passwd = getpass('Password: ')
    if passphrase is None: passphrase = getpass('Passphrase (Empty if no passphrase): ')
    if service is None: service = input('Service: ')
    if service == '':
        ecprint('Service can not be empty', c = 'red')
        return

    if spass is None :
        spass = getpass('Service password (Empty to generate a random one): ')
        if spass != '':
            rspass = getpass('Enter service password again: ')
            if spass != rspass :
                ecprint('Passwords do not match', c = 'red')
                return

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).insert(service, spass)
def listdb(passwd = None, passphrase = None):
    if not os.path.isfile(args.db): ecprint(['database not found', args.db], c = ['red','yellow'], template = '{} {}')
    if not os.path.isfile(args.privkey): ecprint(['privkey not found', args.privkey], c = ['red','yellow'], template = '{} {}')
    if not os.path.isfile(args.pubkey): ecprint(['pubkey not found', args.pubkey], c = ['red','yellow'], template = '{} {}')
    if (not os.path.isfile(args.db)) or (not os.path.isfile(args.privkey)) or (not os.path.isfile(args.pubkey)): return

    if passwd is None : passwd = getpass('Password: ')
    if passphrase is None : passphrase = getpass('Passphrase (Empty if no passphrase): ')
    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).list()
def generate(length = None, alphabet = None):
    kargs = {}
    if length is not None : kargs['length'] = length
    if alphabet is not None : kargs['alphabet'] = alphabet
    ecprint(PasswdManager.passgen(**kargs), c = 'yellow', template = 'Generated password : {}')

if args.command == 'create' :
    if len(args.args) == 1: create(dbfile = args.args[0])
    else: create()

if args.command == 'select' :
    if len(args.args) == 1: select(service = args.args[0])
    else : select()

if args.command == 'insert' :
    if len(args.args) == 1: insert(service = args.args[0])
    elif len(args.args) == 2: insert(service = args.args[0], spass = args.args[1])
    else : insert()

if args.command == 'list' : listdb()

if args.command == 'generate' :
    if len(args.args) == 1: generate(length = args.args[0])
    elif len(args.args) == 2: generate(length = args.args[0], alphabet = args.args[1])
    else : generate()

if args.command == 'session' :
    passwd = getpass('Password: ')
    passphrase = getpass('Passphrase (Empty if no passphrase): ')

    os.system("clear; clear")
    c = ""
    while c != "exit":
        try : c = input('passranoid>> ')
        except :
            os.system('clear; clear')
            break
        else:
            command = c.split(' ')[0]
            arguments = c.split(' ')[1:]

            if command == 'create' :
                rpasswd = getpass('Repeat session password: ')
                if passwd != rpasswd: ecprint('Passwords do not match', c = 'red')
                else :
                    if len(arguments) == 1: create(passwd, passphrase, dbfile = arguments[0])
                    else : create(passwd, passphrase)
            elif command == 'select' :
                if len(arguments) == 1: select(passwd, passphrase, service = arguments[0])
                else : select(passwd, passphrase)
            elif command == 'insert' :
                if len(arguments) == 1: insert(passwd, passphrase, service = arguments[0])
                elif len(arguments) == 2: insert(passwd, passphrase, service = arguments[0], spass = arguments[1])
                else : insert(passwd, passphrase)
            elif command == 'list' : listdb(passwd, passphrase)
            elif command == 'generate' :
                failure = False

                if len(arguments) == 1: length = arguments[0]
                else : length = input('Password length (Empty for default): ')

                if length == '' : length = None
                else :
                    try : length = int(length)
                    except :
                        ecprint('Length must be an integer', c = 'red')
                        failure = True

                if not failure:
                    if len(arguments) == 2: alphabet = arguments[1]
                    else : alphabet = input('Password alphabet (Empty for default): ')

                    if alphabet == '' : alphabet = None
                    else :
                        if '\n' in alphabet:
                            ecprint('Can not use \\n in alphabet', c = 'red')
                            failure = True
                        if '\t' in alphabet:
                            ecprint('Can not use \\t in alphabet', c = 'red')
                            failure = True

                if not failure: generate(length, alphabet)
            elif command == 'clear': os.system('clear; clear')
            elif command == 'help':
                print('Available commands:')
                print('\t-create [dbfile]\n\t\tCreate a new database\n\t\tUse first argument to specify the database file\n')
                print('\t-select [service]\n\t\tSelect a password by service\n\t\tUse first argument to specify the service\n')
                print('\t-insert [service] [password]\n\t\tInsert service and password\n\t\tUse first argument to specify the service\n\t\tUse second argument to specify the password\n')
                print('\t-list\tList services and passwords\n')
                print('\t-generate [length] [alphabet]\n\t\tGenerate a new password\n\t\tUse first argument to specify the length\n\t\tUse second argument to specify the alphabet\n')
                print('\t-clear\tClear the console\n')
                print('\t-help\tShow this help message\n')
                print('\nAll arguments are optional. If missing, they will be asked interactively')
            else : print('Command not found. Type help to see available commands')
    os.system("clear; clear")
