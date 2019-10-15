from os.path import isfile
from getpass import getpass
from easycolor import ecprint

class InputManager:
    @staticmethod
    def doublecheck_getpass():
        passwd = getpass('Password: ')
        rpasswd = getpass('Enter same password again: ')
        if passwd != rpasswd :
            ecprint('Passwords do not match', c = 'red')
            return [False, ""]
        return [True, passwd]

    @staticmethod
    def doublecheck_getpassphrase():
        passphrase = getpass('Passphrase (Empty for no passphrase): ')
        rpassphrase = getpass('Enter same passphrase again: ')
        if passphrase != rpassphrase :
            ecprint('Passphrases do not match', c = 'red')
            return [False, ""]
        return [True, passphrase]

    @staticmethod
    def doublecheck_getservicepass():
        spass = getpass('Service password (Empty to generate a random one): ')
        rspass = getpass('Enter same password again: ')
        if spass != rspass :
            ecprint('Passwords do not match', c = 'red')
            return [False, ""]
        return [True, spass]

    @staticmethod
    def doublecheck_getnewpass():
        passwd = getpass('New password: ')
        rpasswd = getpass('Enter same password again: ')
        if passwd != rpasswd :
            ecprint('Passwords do not match', c = 'red')
            return [False, ""]
        return [True, passwd]

    @staticmethod
    def is_empty(text, text_type):
        if text == '':
            ecprint('{} can not be empty'.format(text_type), c = 'red')
            return True
        return False

    @staticmethod
    def ask_override(file_type, file):
        ecprint('{} {} already exists!'.format(file_type, file), c='yellow')
        ecprint('[y/n]', c = 'yellow', template = 'Do you want to override it? {}: ', end="")
        r = input()
        while r != 'n' and r != 'y':
            ecprint('[y/n]', c = 'yellow', template = 'Do you want to override it? {}: ', end="")
            r = input()
        return (True if r == 'y' else False)

    @staticmethod
    def check_files(db, privkey, pubkey):
        if not isfile(db): ecprint('database {} not found'.format(db), c = 'red')
        if not isfile(privkey): ecprint('privkey {} not found'.format(privkey), c = 'red')
        if not isfile(pubkey): ecprint('pubkey {} not found'.format(pubkey), c = 'red')
        return (False if (not isfile(db)) or (not isfile(privkey)) or (not isfile(pubkey)) else True)

    @staticmethod
    def check_num(num, num_name):
        try : num = int(num)
        except :
            ecprint('{} must be an integer'.format(num_name), c = 'red')
            return [False, 0]
        return [True, num]

    @staticmethod
    def check_alphabet(alphabet):
        if '\n' in alphabet:
            ecprint('Can not use \\n in alphabet', c = 'red')
            return [False, ""]
        if '\t' in alphabet:
            ecprint('Can not use \\t in alphabet', c = 'red')
            return [False, ""]
        if '\\' in alphabet:
            ecprint('Can not use \\ in alphabet', c = 'red')
            return [False, ""]
        return [True, alphabet]
