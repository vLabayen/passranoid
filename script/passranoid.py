#!/usr/bin/python3
import sys
import os
import argparse
from os.path import isfile as isfile
from getpass import getpass
from pmanager import PasswdManager
from imanager import InputManager
from easycolor import ecprint

#TODO: Try to remove a non existing index. Add argument index if solved

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog = '{}'.format('\n'.join([
    'Usage examples :'
    'create         : passranoid.sh create [dbfile]',
    'select         : passranoid.sh select [service]',
    'insert         : passranoid.sh insert [service]',
    'list           : passranoid.sh list',
    'generate       : passranoid.sh generate [length] [alphabet]',
    'session        : passranoid.sh session',
    'version        : passranoid.sh version',
    'changedbpass   : passranoid.sh changedbpass',
    'changekey      : passranoid.sh changekey [newkey]',
    'remove         : passranoid.sh remove [service]'
    '\nAll arguments are optional. If missing, they will be asked interactively'
])))
parser.add_argument('db', help = argparse.SUPPRESS)
parser.add_argument('privkey', help = argparse.SUPPRESS)
parser.add_argument('pubkey', help = argparse.SUPPRESS)
parser.add_argument('command', metavar = 'command', help = 'command to execute. Available options are:\n\t{}'.format('\n\t'.join([
    '- create       : create a new database',
    '- select       : select a password by a service',
    '- insert       : insert a password for a service',
    '- list         : list all passwords and services',
    '- generate     : generate a new password',
    '- session      : open an interactive session',
    '- version      : show passranoid version',
    '- changedbpass : change database password',
    '- changekey    : change database key pair',
    '- remove       : remove a row (or all) by service'
])), choices = ['create', 'select', 'insert', 'list', 'generate', 'session', 'version', 'changedbpass', 'changekey', 'remove'])
parser.add_argument('args', help = argparse.SUPPRESS, nargs = '*')
parser.add_argument('-v', '--verbose', help = 'show info and progress', action = 'store_true', default = False)
args = parser.parse_args()

def create(passwd = None, passphrase = None, dbfile = None):
    db = dbfile if dbfile is not None else args.db
    if isfile(db):
        override = InputManager.ask_override('Database', db)
        if not override : return

    if isfile(args.privkey) and isfile(args.pubkey):
        passphrase = ""                 #Not used in create if keys are not generated
        createRSA = False
    elif not isfile(args.privkey):
        if not isfile('{}.pub'.format(args.privkey)): createRSA = True
        else:
            ecprint('Private key {} is missing!'.format(args.privkey), c='yellow')
            createRSA = InputManager.ask_override('Public key', '{}.pub'.format(args.privkey))
            if not createRSA: return
    elif not isfile(args.pubkey):
        ecprint('Public key {} is missing!'.format(args.pubkey), c='yellow')
        createRSA = InputManager.ask_override('Private key', '{}'.format(args.privkey))
        if not createRSA : return
    else : createRSA = True

    if passwd is None:
        success, passwd = InputManager.doublecheck_getpass()
        if not success : return
    if InputManager.is_empty(passwd, 'Password'): return

    if passphrase is None and createRSA:
        success, passphrase = InputManager.doublecheck_getpassphrase()
        if not success : return

    if args.verbose and not createRSA: ecprint('Using existing rsa key pair', c = 'blue')
    PasswdManager(db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).create(createRSA)
def select(passwd = None, passphrase = None, service = None):
    if not InputManager.check_files(args.db, args.privkey, args.pubkey): return

    if passwd is None: passwd = getpass('Password: ')
    if passphrase is None: passphrase = getpass('Passphrase (Empty if no passphrase): ')
    if service is None: service = input('Service: ')
    if InputManager.is_empty(service, 'Service'): return

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).select(service)
def insert(passwd = None, passphrase = None, service = None):
    if not InputManager.check_files(args.db, args.privkey, args.pubkey): return

    if passwd is None : passwd = getpass('Password: ')
    if passphrase is None: passphrase = getpass('Passphrase (Empty if no passphrase): ')
    if service is None: service = input('Service: ')
    if InputManager.is_empty(service, 'Service'): return
    success, spass = InputManager.doublecheck_getservicepass()
    if not success : return

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).insert(service, spass)
def listdb(passwd = None, passphrase = None):
    if not InputManager.check_files(args.db, args.privkey, args.pubkey): return

    if passwd is None : passwd = getpass('Password: ')
    if passphrase is None : passphrase = getpass('Passphrase (Empty if no passphrase): ')

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).list()
def generate(length = None, alphabet = None):
    kargs = {}

    if length is not None :
        success, kargs['length'] = InputManager.check_num(length, 'Length')
        if not success : return

    if alphabet is not None :
        success, kargs['alphabet'] = InputManager.check_alphabet(alphabet)
        if not success : return
        if InputManager.is_empty(kargs['alphabet'], 'Alphabet'): return


    ecprint(['Generated password :', PasswdManager.passgen(**kargs)], c = ['blue', 'cyan'], template = '{} {}')
def version(passwd = None, passphrase = None):
    if not InputManager.check_files(args.db, args.privkey, args.pubkey): return

    if passwd is None : passwd = getpass('Password: ')
    if passphrase is None : passphrase = getpass('Passphrase (Empty if no passphrase): ')

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).version()
def changedbpass(passwd = None, passphrase = None):
    if not InputManager.check_files(args.db, args.privkey, args.pubkey): return

    if passwd is None: passwd = getpass('Password: ')
    if passphrase is None: passphrase = getpass('Passphrase (Empty if no passphrase): ')
    success, newpasswd = InputManager.doublecheck_getnewpass()
    if not success : return
    if InputManager.is_empty(newpasswd, 'New password') : return

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).changedbpass(newpasswd)
    return newpasswd
def changekey(passwd = None, passphrase = None, newkey = None):
    if not InputManager.check_files(args.db, args.privkey, args.pubkey): return

    if passwd is None: passwd = getpass('Password: ')
    if passphrase is None: passphrase = getpass('Passphrase (Empty if no passphrase): ')
    if newkey is None: newkey = input('New key: ')
    if InputManager.is_empty(newkey, 'New key'): return

    if isfile(newkey) and isfile('{}.pub'.format(newkey)):
        generateRSA = InputManager.ask_override('Key pair', newkey)
        if not generateRSA: ecprint(['Using key pair', newkey], c = ['blue', 'cyan'], template = '{} {}')
    elif isfile(newkey) ^ isfile('{}.pub'.format(newkey)):
        key_aux = [['Private key', newkey], ['Public key', '{}.pub'.format(newkey)]]
        existing, missing = key_aux if isfile(newkey) else key_aux[::-1]
        ecprint('{} {} is missing!'.format(*missing), c = 'yellow')
        generateRSA = InputManager.ask_override(*existing)
        if not generateRSA : return
    else : generateRSA = True

    if generateRSA : newpassphrase = InputManager.doublecheck_getpassphrase()
    else : newpassphrase = passphrase

    PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose).changekey(newkey, generateRSA, newpassphrase)
    return [newkey, '{}.pub'.format(newkey), newpassphrase]
def remove(passwd = None, passphrase = None, service = None):
    if not InputManager.check_files(args.db, args.privkey, args.pubkey): return

    if passwd is None: passwd = getpass('Password: ')
    if passphrase is None: passphrase = getpass('Passphrase (Empty if no passphrase): ')
    if service is None: service = input('Service: ')
    if InputManager.is_empty(service, 'Service'): return

    pwm = PasswdManager(args.db, args.privkey, args.pubkey, passwd, passphrase, args.verbose)
    matches = pwm.countmatches(service)
    if matches == 0: return
    elif matches == 1: pwm.remove(service)
    else:
        removerow = input('Remove at index (* to remove all): ')
        if removerow != '*' :
            success, removerow = InputManager.check_num(removerow, 'Remove index')
            if not success : return
        pwm.remove(service, removerow)

if args.command == 'create' :
    if len(args.args) == 1: create(dbfile = args.args[0])
    else: create()

if args.command == 'select' :
    if len(args.args) == 1: select(service = args.args[0])
    else : select()

if args.command == 'insert' :
    if len(args.args) == 1: insert(service = args.args[0])
    else : insert()

if args.command == 'list' : listdb()

if args.command == 'generate' :
    if len(args.args) == 1: generate(length = args.args[0])
    elif len(args.args) == 2: generate(length = args.args[0], alphabet = args.args[1])
    else : generate()

if args.command == 'version' : version()

if args.command == 'changedbpass' : changedbpass()

if args.command == 'changekey' :
    if len(args.args) == 1: changekey(newkey = args.args[0])
    else : changekey()

if args.command == 'remove' :
    if len(args.args) == 1: remove(service = args.args[0])
    else : remove()

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
                else : insert(passwd, passphrase)
            elif command == 'list' : listdb(passwd, passphrase)
            elif command == 'generate':
                if len(arguments) == 1: length = arguments[0]
                else : length = input('Password length (Empty for default): ')
                if length == '' : length = None

                if len(arguments) == 2: alphabet = arguments[1]
                else : alphabet = input('Password alphabet (Empty for default): ')
                if alphabet == '' : alphabet = None

                generate(length, alphabet)
            elif command == 'version' : version(passwd, passphrase)
            elif command == 'changedbpass' : passwd = changedbpass(passwd, passphrase)
            elif command == 'changekey' :
                if len(arguments) == 1: args.privkey, args.pubkey, passphrase = changekey(passwd, passphrase, newkey = arguments[0])
                else : args.privkey, args.pubkey, passphrase = changekey(passwd, passphrase)
            elif command == 'remove' :
                if len(arguments) == 1: remove(passwd, passphrase, service = arguments[0])
                else : remove(passwd, passphrase)
            elif command == 'clear': os.system('clear; clear')
            elif command == 'help':
                print('Available commands:')
                print('\t-create [dbfile]\n\t\tCreate a new database\n\t\tUse first argument to specify the database file\n')
                print('\t-select [service]\n\t\tSelect a password by service\n\t\tUse first argument to specify the service\n')
                print('\t-insert [service] [password]\n\t\tInsert service and password\n\t\tUse first argument to specify the service\n\t\tUse second argument to specify the password\n')
                print('\t-list\tList services and passwords\n')
                print('\t-generate [length] [alphabet]\n\t\tGenerate a new password\n\t\tUse first argument to specify the length\n\t\tUse second argument to specify the alphabet\n')
                print('\t-version\tPrint passranoid version\n')
                print('\t-changedbpass\tChange database password\n')
                print('\t-changekey\n\t\tChange database key pair\n\t\tUse first argument to specify the name of the private key\n\t\tThe public key is supposed to be the same name ended with .pub\n')
                print('\t-remove\n\t\tRemove a row (or all) by service\n\t\tUse first argument to specify the service to remove\n')
                print('\t-clear\tClear the console\n')
                print('\t-help\tShow this help message\n')
                print('\nAll arguments are optional. If missing, they will be asked interactively')
            else : print('Command not found. Type help to see available commands')
    os.system("clear; clear")
