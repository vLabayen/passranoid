import sys
import yaml
import readline
from os import R_OK, W_OK
from os import popen, environ, listdir, access, remove
from os.path import isdir, isfile
from getpass import getpass
from printer import cprint, cprepare

class CommandManager:
    def __init__(self, configfile, databases_path, keys_path):
        self.configfile = configfile
        if not isfile(self.configfile): self.config = {}
        else : self.config = yaml.safe_load(open(self.configfile, 'r'))

        self.databases_path = databases_path
        self.keys_path = keys_path
        self.using = None
        self.auth = None

        self.commands = sorted([
            'create', 'import', 'passgen', 'clear', 'help',
            'use', 'select', 'insert', 'remove', 'list',
            'changedbpass', 'changedbkey', 'export', 'version',
            'exit'
        ])
        self.commands_usage = {
            'create' : 'usage : create [dbname]',
            'import' : 'usage : import [dbfile] [dbname]',
            'passgen' : 'usage : passgen [length] [alphabet]',
            'use' : 'usage : use [dbname]',
            'select' : 'usage : select [service]',
            'insert' : 'usage : insert [service] [user]',
            'remove' : 'usage : remove [index]',
            'export' : 'usage : export [dbfile]'
        }
        self.commands_args_help = {
            'import' : {1 : 'ls'},
            'use' : {1 : 'existing_dbs'},
            'export' : {1 : 'ls'}
        }
        self.cache = []
        self.autocompletion = True
        readline.set_completer(self.autocomplete)
        readline.parse_and_bind('tab: complete')
        readline.set_completion_display_matches_hook(self.displaymatches)

    def autocomplete(self, text, state):
        if state == 0: # on first trigger, build possible matches
            if not self.autocompletion : return None
            else :
                buf = readline.get_line_buffer()
                if any([buf.startswith(c) for c in self.commands]) :
                    self.cache = ['-', '_']
                    return self.cache[0]
                else: options = self.commands

            if text: self.cache = [o for o in options if o.startswith(text)]
            else : self.cache = options

        try : return self.cache[state]
        except IndexError : return None

    def displaymatches(self, substitution, matches, longest_match_length):
        line_buffer = readline.get_line_buffer()
        columns = int(popen('stty size', 'r').read().split()[1])
        print()

        if matches == ['-', '_'] : self.incommand_help(line_buffer, columns)
        else :
            template = '{}{}{}'.format('{:<', int(longest_match_length * 1.2), '}')
            display = [""]
            for match in matches:
                match = template.format(match)
                if len(display[-1]) + len(match) > columns: display.append("")
                display[-1] += match

            for line in display: print(line)

            print("passranoid>> {}".format(line_buffer), end="")
            sys.stdout.flush()

    def incommand_help(self, line_buffer, columns):
        buf = line_buffer.split(' ')
        if len(buf) == 1:
            try : h = self.commands_usage[buf[0]]
            except : pass
            else : print(h)
        else:
            arg_index = len(buf[1:])
            try : h = self.commands_args_help[buf[0]][arg_index]
            except : pass
            else :
                if h ==  'existing_dbs':
                    searching_pattern = buf[arg_index]
                    options = list(self.config.keys())
                elif h == 'ls' :
                    paths = buf[arg_index].split('/')
                    search_dir = '/'.join(p for p in paths[:-1] if p != '')
                    searching_pattern = paths[-1]
                    if buf[arg_index].startswith('/') : search_dir = '/{}'.format(search_dir)

                    if search_dir == '' : options = listdir()
                    else : options = listdir(search_dir)
                    options += ['.', '..']

                if len(options) == 0: longest_match_length = 0
                else : longest_match_length = max(map(len, options))
                match_print_len = int(longest_match_length + 3)
                template = '{}{}{}'.format('{:<', match_print_len, '}')

                options = [o for o in options if o.startswith(searching_pattern)]
                if h == 'ls' and not searching_pattern.startswith('.'): options = [o for o in options if not o.startswith('.')]

                if len(options) == 1:
                    readline.insert_text(options[0][len(searching_pattern):])
                    if h == 'ls':
                        full_path = '{}/{}'.format(search_dir, options[0]) if search_dir != '' else options[0]
                        if isdir(full_path): readline.insert_text('/')
                elif len(options) > 0:
                    common_start = options[0][0:([min([elem==seq[0] for elem in seq]+[True]) for seq in zip(*options)] + [False]).index(False)]
                    if common_start != '': readline.insert_text(common_start[len(searching_pattern):])

                    if h == 'ls':
                        path_template = '{}/{}'.format(search_dir, '{}') if search_dir != '' else '{}'
                        options = [(cprepare(template.format('{}/'.format(o)), color = 'lblue') if isdir(path_template.format(o)) else template.format(o)) for o in options]
                    else : options = [template.format(o) for o in options]

                    display = [""]
                    display_len = 0
                    for o in options:
                        if (display_len + match_print_len) > columns:
                            display.append("")
                            display_len = 0
                        display[-1] += o
                        display_len += match_print_len

                    for line in display : print(line)

        print("passranoid>> {}".format(line_buffer), end="")
        sys.stdout.flush()

    def input(self, prompt, history = True):
        t = input(prompt)
        if not history and t != '': readline.remove_history_item(readline.get_current_history_length() - 1)
        return t

    def is_something_writed(self): return (readline.get_line_buffer() != '')

    def add_db(self, dbname, newconf):
        if dbname in self.config:
            CommandManager.error('The database already exists')
            return False
        self.config[dbname] = newconf
        return True

    def remove_db(self, dbname):
        if not dbname in self.config:
            CommandManager.error('The database does not exists')
            return False

        rconf = self.config.pop(dbname)

        if isfile(rconf['dbfile']):
            try : os.remove(rconf['dbfile'])
            except :
                CommandManager('Can not remove db {}'.format(rconf['dbfile']))
                return False
        return True

    def save_config(self):
        try : yaml.dump(self.config, open(self.configfile, 'w'), default_flow_style=False, allow_unicode=True)
        except :
            CommandManager.error('Error writing to the config file {}'.format(self.configfile))
            return False
        return True

    def get_db(self, dbname):
        if dbname not in self.config:
            CommandManager.error('The database does not exists')
            return [False, {}]

        conf = self.config[dbname]
        for filetype, file in conf.items():
            if not isfile(file):
                CommandManager.error('{} {} not found'.format(filetype.capitalize(), file))
                return [False, {}]

        return [True, conf]

    def get_using_db(self):
        if self.using is None:
            CommandManager.error('No database in use')
            return [False, {}]

        for filetype, file in self.using.items():
            if not isfile(file):
                CommandManager.error('{} {} not found'.format(filetype.capitalize(), file))
                return [False, {}]

        return [True, self.using]

    def set_auth(self, conf, passwd, passphrase):
        if not conf == self.using:
            CommandManager.error('Can not set auth. Incorrect database')
            return False

        if CommandManager.is_empty(passwd, 'Password can not be empty'): return
        self.auth = {'passwd' : passwd, 'passphrase' : passphrase}


    @staticmethod
    def error(text):
        cprint(text, color = 'red')

    @staticmethod
    def is_empty(text, error_log):
        if text == '':
            CommandManager.error(error_log)
            return True
        return False

    @staticmethod
    def do_not_match(a, b, error_log):
        if a != b:
            CommandManager.error(error_log)
            return True
        return False

    @staticmethod
    def cast_to_int(num, error_log):
        try : num = int(num)
        except ValueError:
            CommandManager.error(error_log)
            return [False, num]
        return [True, num]

    @staticmethod
    def getpasswd(doublecheck = False, auth = None):
        passwd = None
        if auth is not None:
            try : passwd = auth['passwd']
            except: pass

        if passwd is None:
            passwd = getpass('Password: ')

            if doublecheck:
                rpasswd = getpass('Enter same password again: ')
                if CommandManager.do_not_match(passwd, rpasswd, 'Passwords do not match'): return [False, ""]

            if CommandManager.is_empty(passwd, 'Password can not be empty'): return [False, ""]

        return [True, passwd]

    @staticmethod
    def getpassphrase(doublecheck = False, auth = None):
        passphrase = None
        if auth is not None :
            try : passphrase = auth['passphrase']
            except : pass

        if passphrase is None:
            passphrase = getpass('Passphrase (Empty for no passphrase): ')

            if doublecheck:
                rpassphrase = getpass('Enter same passphrase again: ')
                if CommandManager.do_not_match(passphrase, rpassphrase, 'Passphrases do not match'): return [False, ""]

        return [True, passphrase]

    @staticmethod
    def getservicepasswd(doublecheck = False):
        spasswd = getpass('Service password (Empty to generate a random one): ')

        if doublecheck :
            rspasswd = getpass('Enter same password again: ')
            if CommandManager.do_not_match(spasswd, rspasswd, 'Passwords do not match'): return [False, ""]

        return [True, spasswd]

    @staticmethod
    def getnewpasswd(doublecheck = False):
        passwd = getpass('New password: ')

        if doublecheck:
            rpasswd = getpass('Enter same password again: ')
            if CommandManager.do_not_match(passwd, rpasswd, 'Passwords do not match'): return [False, ""]

        if CommandManager.is_empty(passwd, 'Password can not be empty'): return [False, ""]
        return [True, passwd]

    @staticmethod
    def getnewpassphrase(doublecheck = False):
        passphrase = getpass('New passphrase (Empty for no passphrase): ')

        if doublecheck:
            rpassphrase = getpass('Enter same passphrase again: ')
            if CommandManager.do_not_match(passphrase, rpassphrase, 'Passphrases do not match'): return [False, ""]

        return [True, passphrase]

    @staticmethod
    def checkpermision(file, permission_type):
        if CommandManager.is_empty(file, 'The file can not be empty'): return False

        if permission_type == 'r':
            if not isfile(file):
                CommandManager.error('File not found {}'.format(file))
                return False
            if not access(file, R_OK):
                CommandManager.error('Read permission denied {}'.format(file))
                return False

        elif permission_type == 'w':
            if isfile(file):
                if not access(file, W_OK):
                    CommandManager.error('Write permission denied {}'.format(file))
                    return False
            else:
                paths = file.split('/')
                if len(paths) == 1:
                    if not access('.', W_OK):
                        CommandManager.error('Write permission denied {}'.format(file))
                        return False
                else :
                    if len(paths[:-1]) == 1 and file.startswith('/'): dirpath = '/'
                    else : dirpath = '/'.join(paths[:-1])
                    if not access(dirpath, W_OK):
                        CommandManager.error('Write permission denied {}'.format(file))
                        return False

        else : raise TypeError('Unknown permission type')
        return True



    def handle(self, command, args):
        self.autocompletion = False

        try:
            if command == 'create': command_args = self._create(args)
            elif command == 'use' : command_args = self._use(args)
            elif command == 'insert' : command_args = self._insert(args)
            elif command == 'list' : command_args = self._list()
            elif command == 'select' : command_args = self._select(args)
            elif command == 'remove' : command_args = self._remove(args)
            elif command == 'version' : command_args = self._version()
            elif command == 'passgen' : command_args = self._passgen(args)
            elif command == 'changedbpass' : command_args = self._changedbpass()
            elif command == 'changedbkey' : command_args = self._changedbkey()
            elif command == 'export' : command_args = self._exportdb(args)
            elif command == 'import' : command_args = self._importdb(args)
            else: raise ValueError('Unknown command')
        except (KeyboardInterrupt, EOFError) as e:
            self.autocompletion = True
            raise e

        self.autocompletion = True
        return command_args

    def _create(self, args):
        #dbname
        if len(args) >= 1: dbname = args[0]
        else: dbname = self.input('dbname: ', history = False)
        if CommandManager.is_empty(dbname, 'The database name can not be empty'): return False

        success = self.add_db(dbname, {
            'dbfile' : '{}/{}'.format(self.databases_path, dbname),
            'privkey' : '{}/{}'.format(self.keys_path, dbname),
            'pubkey' : '{}/{}.pub'.format(self.keys_path, dbname)
        })
        if not success : return False

        #passwd and passphrase
        success, passwd = CommandManager.getpasswd(doublecheck = True)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(doublecheck = True)
        if not success : return False

        if not self.save_config():
            self.remove_db(dbname)
            return False

        return [dbname, passwd, passphrase, self.databases_path, self.keys_path]

    def _use(self, args):
        #dbname
        if len(args) >= 1: dbname = args[0]
        else : dbname = self.input('dbname: ', history = False)
        if CommandManager.is_empty(dbname, 'The database name can not be empty'): return False

        #config
        success, conf = self.get_db(dbname)
        if not success : return False

        #passwd and passphrase
        success, passwd = CommandManager.getpasswd()
        if not success : return False
        success, passphrase = CommandManager.getpassphrase()
        if not success : return False

        self.using = conf
        return [conf, passwd, passphrase]

    def _insert(self, args):
        success, conf = self.get_using_db()
        if not success : return False

        if len(args) >= 1: service = args[0]
        else : service = self.input('service: ', history = False)
        if CommandManager.is_empty(service, 'The service can not be empty'): return False

        if len(args) >= 2: user = args[1]
        else : user = self.input('user: ', history = False)
        if CommandManager.is_empty(user, 'The user can not be empty'): return False

        success, spasswd = CommandManager.getservicepasswd(doublecheck = True)
        if not success : return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, service, user, spasswd, passwd, passphrase]

    def _list(self):
        success, conf = self.get_using_db()
        if not success : return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, passwd, passphrase]

    def _select(self, args):
        success, conf = self.get_using_db()
        if not success : return False

        if len(args) >= 1: service = args[0]
        else: service = self.input('service: ', history = False)
        if CommandManager.is_empty(service, 'The service can not be empty'): return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, service, passwd, passphrase]

    def _remove(self, args):
        success, conf = self.get_using_db()
        if not success : return False

        if len(args) >= 1: index = args[0]
        else : index = self.input('Row index (Use * for all): ', history = False)
        if CommandManager.is_empty(index, 'The index can not be empty'): return False
        if index != '*':
            success, index = CommandManager.cast_to_int(index, 'Index must be either * or an integer')
            if not success : return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, index, passwd, passphrase]

    def _version(self):
        success, conf = self.get_using_db()
        if not success : return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, passwd, passphrase]

    def _passgen(self, args):
        if len(args) >= 1: length = args[0]
        else : length = self.input('Password length: ', history = False)
        if CommandManager.is_empty(length, 'The length can not be empty'): return False
        success, length = CommandManager.cast_to_int(length, 'Length must be an integer')
        if not success : return False

        if len(args) >= 2: alphabet = args[1]
        else : alphabet = self.input('Password alphabet (Empty to default): ', history = False)

        return [length, alphabet]

    def _changedbpass(self):
        success, conf = self.get_using_db()
        if not success : return False

        success, newpasswd = CommandManager.getnewpasswd(doublecheck = True)
        if not success : return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        self.auth['passwd'] = newpasswd
        return [conf, newpasswd, passwd, passphrase]

    def _changedbkey(self):
        success, conf = self.get_using_db()
        if not success : return False

        success, newpassphrase = CommandManager.getnewpassphrase(doublecheck = True)
        if not success : return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        self.auth['passphrase'] = newpassphrase
        return [conf, newpassphrase, passwd, passphrase]

    def _exportdb(self, args):
        success, conf = self.get_using_db()
        if not success : return False

        if len(args) >= 1: dbfile = args[0]
        else : dbfile = self.input('export file: ', history = False)
        if not CommandManager.checkpermision(dbfile, 'w'): return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, dbfile, passwd, passphrase]

    def _importdb(self, args):
        success, conf = self.get_using_db()
        if not success : return False

        if len(args) >= 1: dbfile = args[0]
        else : dbfile = self.input('export file: ', history = False)
        if not CommandManager.checkpermision(dbfile, 'r'): return False

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, dbfile, passwd, passphrase]
