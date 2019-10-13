from giltzarrapo import Giltzarrapo
from getpass import getpass, getuser
from easycolor import ecprint
from random import randint

class PasswdManager:
    Default_Alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!¡()?¿{}[]<>|@#$%&/=+*-_.:;,'
    Default_Length = 20

    def __init__(self, db, privkey, pubkey, passwd, passphrase, verbose = False):
        self.db = db
        self.privkey = privkey
        self.pubkey = pubkey
        self.passwd = passwd
        self.passphrase = passphrase
        self.verbose = verbose

    @staticmethod
    def passgen(length = Default_Length, alphabet = Default_Alphabet):
        return ''.join([alphabet[randint(0, len(alphabet) - 1)] for _ in range(length)])

    def create(self, createRSA = False):
        if self.verbose is True: ecprint('Creating database', c = 'blue')
        g = Giltzarrapo()
        newline = bytes('passranoid_database\tversion:1\n', encoding = 'utf-8')
        #Append new full blocks
        while len(newline) > g.chunkSize:
            g.blocks.append(newline[0:g.chunkSize])
            newline = newline[g.chunkSize:]
        #Add the remaining part of the new line
        if len(newline) > 0: g.blocks.append(newline)
        g.status = 'plain'

        if createRSA is True:
            if self.verbose is True: ecprint('Creating rsa key pair', c = 'blue')
            keyargs = {'dir' : '/'.join(self.privkey.split('/')[:-1]), 'name' : self.privkey.split('/')[-1]}
            privkey, pubkey = Giltzarrapo.generateRSApair(self.passphrase, **{k : v for k,v in keyargs.items() if v is not ""})
            if self.verbose is True:
                ecprint(['Your identification has been saved in', privkey], c = ['blue', 'yellow'], template = '{} {}')
                ecprint(['Your public key has been save in', pubkey], c = ['blue', 'yellow'], template = '{} {}')
        else: pubkey = self.pubkey

        g.encrypt(self.passwd, pubkey).save(self.db)
        if self.verbose is True: ecprint(['Database saved in', self.db], c = ['blue', 'yellow'], template = '{} {}')

    def select(self, service, refresh_db = True):

        #Read and decrypt the file
        if self.verbose : ecprint('Reading database', c='blue')
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)
        lines = [l for b in g.blocks for l in b.decode('utf-8').split('\n')[:-1]]
        #Search for required service
        ecprint('QUERY MATCH', c = 'blue', template = '{}{}{}'.format(19*'*', '{}', 18*'*'))
        for line in lines[1:]:
            serv, passw = line.split('\t')
            if service == serv: ecprint([serv, passw], c = 'yellow', template = '{} : {}')
        print(48 * '*')

        #Refresh db
        if refresh_db :
            if self.verbose : ecprint('Refreshing database', c = 'blue')
            g.encrypt(self.passwd, self.pubkey).save(self.db)

    def insert(self, service, password = ""):
        if password == "":
            password = PasswdManager.passgen()
            ecprint(password, c = 'yellow', template = 'Generated password : {}')

        #Read and decrypt the file
        if self.verbose : ecprint('Reading database', c='blue')
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)

        if self.verbose : ecprint('Inserting service', c='blue')
        #Prepare new line
        newline = bytes('{}\t{}\n'.format(service, password), encoding = 'utf-8')
        b, l = len(g.blocks[-1]), len(newline)

        #try to fill the last block
        if l > (g.chunkSize - b):
            g.blocks[-1] = g.blocks[-1] + newline[0:g.chunkSize - b]
            newline = newline[g.chunkSize - b:]
        else :
            g.blocks[-1] = g.blocks[-1] + newline[0:l]
            newline = newline[l:]
        #Append new full blocks
        while len(newline) > g.chunkSize:
            g.blocks.append(newline[0:g.chunkSize])
            newline = newline[g.chunkSize:]
        #Add the remaining part of the new line
        if len(newline) > 0: g.blocks.append(newline)

        #Save the file
        if self.verbose : ecprint('Saving modified database', c='blue')
        g.encrypt(self.passwd, self.pubkey).save(self.db)

    def list(self, refresh_db = True):
        #Read and decrypt the file
        if self.verbose : ecprint('Reading database', c='blue')
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)
        lines = [l for b in g.blocks for l in b.decode('utf-8').split('\n')[:-1]]
        #lsit services and passwords
        ecprint('DATABASE', c = 'blue', template = '{}{}{}'.format(20*'*', '{}', 20*'*'))
        if len(lines[1:]) == 0: ecprint('No services stored', c = 'yellow')
        for line in lines[1:]: print('{} : {}'.format(*line.split('\t')))
        print(48 * '*')

        #Refresh db
        if refresh_db :
            if self.verbose : ecprint('Refreshing database', c = 'blue')
            g.encrypt(self.passwd, self.pubkey).save(self.db)
