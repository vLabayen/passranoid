#!/usr/bin/python3
import sys
import os
from os.path import isfile as isfile
from getpass import getpass
from pmanager import PasswdManager
from cmanager import CommandManager
from printer import cprint, cprepare, ctable

#TODO : remove database
#TODO : change service user
#TODO : change service passwd
#TODO : merge databases

def print_help(in_session = True):
    title_color = {'color' : 'default', 'mode' : 'bold'}
    primary_color = {'color' : 'blue', 'mode' : 'bold'}
    secundary_color = {'color' : 'blue', 'mode' : 'normal'}
    tertiary_color = {'color' : 'lgray', 'mode' : 'normal'}

    if not in_session :
        print(cprepare('Usage :', **title_color), cprepare('./passranoid.sh', **primary_color))
        print(cprepare('Options :', **title_color))
        print(cprepare('    -v, --verbose', **primary_color), cprepare(': Open session in verbose mode', **secundary_color))
        print(cprepare('    -h, --help', **primary_color), cprepare(': Print this message and exit\n', **secundary_color))

    print(cprepare('Available commands {} :\n'.format('' if in_session else 'in session mode'), **title_color))

    print(cprepare('  create [dbname]', **primary_color), cprepare(': Create a new database', **secundary_color))
    print(cprepare('      dbname : New database name', **tertiary_color))
    print(cprepare('  import [dbfile]', **primary_color), cprepare(': Import a exported database into the one in use', **secundary_color))
    print(cprepare('      dbfile : Exported database file to import', **tertiary_color))
    print(cprepare('  passgen [length] [alphabet]', **primary_color), cprepare(': Generate a new password', **secundary_color))
    print(cprepare('      length : Length of the generated password', **tertiary_color))
    print(cprepare('      alphabet : Alphabet of the generated password', **tertiary_color))
    print(cprepare('  Ctrl+L/clear', **primary_color), cprepare(': Clear the console', **secundary_color))
    print(cprepare('  help', **primary_color), cprepare(': Show this help message', **secundary_color))
    print(cprepare('  use [dbname]', **primary_color), cprepare(': Load a database', **secundary_color))
    print(cprepare('      dbname : Name of the database to load', **tertiary_color))
    print(cprepare('  add/insert [service] [user]', **primary_color), cprepare(': Insert a new entry', **secundary_color))
    print(cprepare('      service : Name of the service to insert', **tertiary_color))
    print(cprepare('      user : Name of the username/email of the service', **tertiary_color))
    print(cprepare('  select [service]', **primary_color), cprepare(': Select entries by service', **secundary_color))
    print(cprepare('      service : Name of the service to select', **tertiary_color))
    print(cprepare('  rm/remove [index]', **primary_color), cprepare(': Remove entries by index', **secundary_color))
    print(cprepare('      index : The index of the entry to remove', **tertiary_color))
    print(cprepare('  ls/list', **primary_color), cprepare(': List all the entries in the loaded database', **secundary_color))
    print(cprepare('  changedbpass', **primary_color), cprepare(': Change the password of the loaded database', **secundary_color))
    print(cprepare('  changedbkey', **primary_color), cprepare(': Change the rsa pair of the loaded database', **secundary_color))
    print(cprepare('  export [dbfile]', **primary_color), cprepare(': Export loaded database', **secundary_color))
    print(cprepare('      dbfile : Name of the file to save the exported database', **tertiary_color))
    print(cprepare('  version', **primary_color), cprepare(': Show current version of the database', **secundary_color))
    print(cprepare('  Crtl+C/Ctrl+D/exit', **primary_color), cprepare(': Exit session mode', **secundary_color))

    print(cprepare('\nAll arguments are optional. If missing, they will be asked interactively', **title_color))
def clear(): os.system('clear; clear')


if ('-h' in sys.argv) or ('--help' in sys.argv):
    print_help(in_session = False)
    sys.exit()
if ('-v' in sys.argv) or ('--verbose' in sys.argv):
    if '-v' in sys.argv : sys.argv.remove('-v')
    if '--verbose' in sys.argv : sys.argv.remove('--verbose')
    verbose = True
else : verbose = False

PasswdManager.verbose = verbose
cm = CommandManager(*sys.argv[1:4])

clear()
command = ""
while command != "exit":
    try : command = cm.im.input('passranoid>> ')
    except KeyboardInterrupt:
        if not cm.im.is_something_writed(): break
        else : print('^C')
    except : break
    else :
        command, args = command.split(' ')[0], command.split(' ')[1:]
        try :
            if command == 'create' :
                create_args = cm.handle(command, args)
                if create_args != False: PasswdManager.create(*create_args)
            elif command == 'import':
                import_args = cm.handle(command, args)
                if import_args != False: PasswdManager.importdb(*import_args)
            elif command == 'passgen' :
                passgen_args = cm.handle(command, args)
                if passgen_args != False:
                    newpasswd = PasswdManager.passgen(*passgen_args)
                    cprint('Generated password : ', color = 'blue', end = "")
                    cprint(newpasswd, color = 'lblue')
            elif command == 'clear' : clear()
            elif command == 'help' : print_help()
            elif command == 'use':
                verify_args = cm.handle(command, args)
                if verify_args != False:
                    success = PasswdManager.verifyauth(*verify_args)
                    if not success : cprint('Wrong password or/and passphrase', color = 'red')
                    else : cm.set_auth(*verify_args)
            elif command == 'insert' or command == 'add':
                insert_args = cm.handle('insert', args)
                if insert_args != False: PasswdManager.insert(*insert_args)
            elif command == 'select':
                select_args = cm.handle(command, args)
                if select_args != False:
                    query_match = PasswdManager.select(*select_args)
                    if len(query_match) > 0: ctable(
                        header = ['id', 'service', 'user', 'password'],
                        data = [([i] + l.split('\t')) for i,l in query_match],
                        header_color = 'blue', rows_color = 'lblue'
                    )
                    else : cprint('No matches', color = 'orange')
            elif command == 'remove' or command == 'rm':
                remove_args = cm.handle('remove', args)
                if remove_args != False :
                    success = PasswdManager.remove(*remove_args)
                    if not success : cprint('The index does not exists', color = 'red')
            elif command == 'list' or command == 'ls':
                list_args = cm.handle('list', args)
                if list_args != False:
                    entries = PasswdManager.list(*list_args)
                    if len(entries) > 0: ctable(
                        header = ['id', 'service', 'user', 'password'],
                        data = [([i] + l.split('\t')) for i,l in entries],
                        header_color = 'blue', rows_color = 'lblue'
                    )
                    else : cprint('No entries', color = 'orange')
            elif command == 'changedbpass' :
                changedbpass_args = cm.handle(command, args)
                if changedbpass_args != False: PasswdManager.changedbpass(*changedbpass_args)
            elif command == 'changedbkey' :
                changedbkey_args = cm.handle(command, args)
                if changedbkey_args != False : PasswdManager.changedbkey(*changedbkey_args)
            elif command == 'export' :
                export_args = cm.handle(command, args)
                if export_args != False:
                    success = PasswdManager.exportdb(*export_args)
                    if not success: cprint('The database contains no rows to export', color = 'red')
            elif command == 'version' :
                version_args = cm.handle(command, args)
                if version_args != False:
                    for vtype in PasswdManager.version(*version_args).split('\t'):
                        cprint(vtype, color = 'lblue')
            elif command == 'exit' : pass
            elif command == '' : pass
            else : cprint('Unknown command {}'.format(command), color = 'red')
        except KeyboardInterrupt: print('^C')
        except EOFError: print('^D')

clear()
