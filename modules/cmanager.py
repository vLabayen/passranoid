import sys
import yaml
import readline
from os import R_OK, W_OK
from os import popen, listdir, access, remove
from os.path import isdir, isfile
from getpass import getpass
from printer import cprint, cprepare
from imanager import InputManager

class CommandManager:
    def __init__(self, configfile, databases_path, keys_path):
        self.configfile = configfile
        if not isfile(self.configfile): self.config = {}
        else : self.config = yaml.safe_load(open(self.configfile, 'r'))

        self.databases_path = databases_path
        self.keys_path = keys_path
        self.using = None
        self.auth = None

        self.im = InputManager(self.config)

    def can_add_db(self, dbname, error_log):
        if dbname in self.config:
            CommandManager.error(error_log)
            return False
        return True

    def add_db(self, dbname, newconf):
        if dbname in self.config:
            CommandManager.error('The database already exists')
            return False

        self.config[dbname] = newconf

        if not self.save_config():
            self.remove_db(dbname)
            return False
        return True

    def remove_db(self, dbname):
        if not dbname in self.config:
            CommandManager.error('The database does not exists')
            return False

        rconf = self.config.pop(dbname)

        if isfile(rconf['dbfile']):
            try : os.remove(rconf['dbfile'])
            except :
                CommandManager.error('Can not remove db {}'.format(rconf['dbfile']))
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

        if CommandManager.is_empty(passwd, 'Password can not be empty'): return False
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
        self.im.autocompletion = False

        while True:
            try : args.remove('')
            except ValueError: break

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
        except (KeyboardInterrupt, EOFError) as e: raise e
        finally : self.im.clear_buffer(autocompletion = True)


        return command_args

    def _create(self, args):
        #dbname
        if len(args) >= 1: dbname = args[0]
        else: dbname = self.im.input('dbname: ', history = False)
        if CommandManager.is_empty(dbname, 'The database name can not be empty'): return False
        if not self.can_add_db(dbname, 'The database already exists'): return False

        #passwd and passphrase
        success, passwd = CommandManager.getpasswd(doublecheck = True)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(doublecheck = True)
        if not success : return False

        success = self.add_db(dbname, {
            'dbfile' : '{}/{}'.format(self.databases_path, dbname),
            'privkey' : '{}/{}'.format(self.keys_path, dbname),
            'pubkey' : '{}/{}.pub'.format(self.keys_path, dbname)
        })
        if not success : return False

        return [dbname, passwd, passphrase, self.databases_path, self.keys_path]

    def _use(self, args):
        #dbname
        self.im.set_buffer(buffer = 'use ', prompt = 'dbname: ')
        if len(args) >= 1: dbname = args[0]
        else : dbname = self.im.input('dbname: ', history = False)
        if CommandManager.is_empty(dbname, 'The database name can not be empty'): return False
        self.im.clear_buffer()

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
        else : service = self.im.input('service: ', history = False)
        if CommandManager.is_empty(service, 'The service can not be empty'): return False

        if len(args) >= 2: user = args[1]
        else : user = self.im.input('user: ', history = False)
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
        else: service = self.im.input('service: ', history = False)
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
        else : index = self.im.input('Row index (Use * for all): ', history = False)
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
        else : length = self.im.input('Password length: ', history = False)
        if CommandManager.is_empty(length, 'The length can not be empty'): return False
        success, length = CommandManager.cast_to_int(length, 'Length must be an integer')
        if not success : return False

        if len(args) >= 2: alphabet = args[1]
        else : alphabet = self.im.input('Password alphabet (Empty to default): ', history = False)

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

        self.im.set_buffer(buffer = 'export ', prompt = 'export file: ')
        if len(args) >= 1: dbfile = args[0]
        else : dbfile = self.im.input('export file: ', history = False)
        if not CommandManager.checkpermision(dbfile, 'w'): return False
        self.im.clear_buffer()

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, dbfile, passwd, passphrase]

    def _importdb(self, args):
        success, conf = self.get_using_db()
        if not success : return False

        self.im.set_buffer(buffer = 'import ', prompt = 'import file: ')
        if len(args) >= 1: dbfile = args[0]
        else : dbfile = self.im.input('import file: ', history = False)
        if not CommandManager.checkpermision(dbfile, 'r'): return False
        self.im.clear_buffer()

        success, passwd = CommandManager.getpasswd(auth = self.auth)
        if not success : return False
        success, passphrase = CommandManager.getpassphrase(auth = self.auth)
        if not success : return False

        return [conf, dbfile, passwd, passphrase]
