#!/usr/bin/python3
import sys
import os
from os.path import isfile as isfile
from getpass import getpass
from pmanager import PasswdManager
from cmanager import CommandManager
from printer import cprint, ctable

#TODO : ask for passwd and passphrase in use and bypass the others
#TODO : autocompletion inside formularies
#TODO : arreglar bug de parametro vacio al acabar comando con espacio
#TODO : arreglar bug ctable
#TODO : remove database
#TODO : change service user
#TODO : change service passwd
#TODO : merge databases

def print_help(in_session = True):
    if not in_session :
        cprint('Usage : ./passranoid.sh')
        cprint('Options :')
        cprint('    -v, --verbose : Open session in verbose mode')
        cprint('    -h, --help : Print this message and exit\n')

    cprint('Available commands {} :\n'.format('' if in_session else 'in session mode'))

    cprint('  create [dbname] : Create a new database', mode = 'bold', color = 'blue')
    cprint('      dbname : New database name')
    cprint('  import [dbfile] : Import a exported database into the one in use', mode = 'bold', color = 'blue')
    cprint('      dbfile : Exported database file to import')
    cprint('  passgen [length] [alphabet] : Generate a new password', mode = 'bold', color = 'blue')
    cprint('      length : Length of the generated password')
    cprint('      alphabet : Alphabet of the generated password')
    cprint('  clear : Clear the console', mode = 'bold', color = 'blue')
    cprint('  help : Show this help message', mode = 'bold', color = 'blue')
    cprint('  use [dbname] : Load a database', mode = 'bold', color = 'blue')
    cprint('      dbname : Name of the database to load')
    cprint('  insert [service] [user] : Insert a new entry', mode = 'bold', color = 'blue')
    cprint('      service : Name of the service to insert')
    cprint('      user : Name of the username/email of the service')
    cprint('  select [service] : Select entries by service', mode = 'bold', color = 'blue')
    cprint('      service : Name of the service to select')
    cprint('  remove [index] : Remove entries by index', mode = 'bold', color = 'blue')
    cprint('      index : The index of the entry to remove')
    cprint('  list : List all the entries in the loaded database', mode = 'bold', color = 'blue')
    cprint('  changedbpass : Change the password of the loaded database', mode = 'bold', color = 'blue')
    cprint('  changedbkey : Change the rsa pair of the loaded database', mode = 'bold', color = 'blue')
    cprint('  export [dbfile] : Export loaded database', mode = 'bold', color = 'blue')
    cprint('      dbfile : Name of the file to save the exported database')
    cprint('  version : Show current version of the database', mode = 'bold', color = 'blue')
    cprint('  exit : Exit session mode', mode = 'bold', color = 'blue')

    cprint('\nAll arguments are optional. If missing, they will be asked interactively')
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
    try : command = cm.input('passranoid>> ')
    except KeyboardInterrupt:
        if not cm.is_something_writed(): break
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
            elif command == 'use': cm.handle(command, args)
            elif command == 'insert':
                insert_args = cm.handle(command, args)
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
            elif command == 'remove':
                remove_args = cm.handle(command, args)
                if remove_args != False :
                    success = PasswdManager.remove(*remove_args)
                    if not success : cprint('The index does not exists', color = 'red')
            elif command == 'list':
                list_args = cm.handle(command, args)
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
                if export_args != False: PasswdManager.exportdb(*export_args)
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
