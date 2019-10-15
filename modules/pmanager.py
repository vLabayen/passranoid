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
        newline = bytes('passranoid_database:v1.1\tpassranoid_interface:v1.1\tpassranoid_config:v0\n', encoding = 'utf-8')
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
                ecprint(['Your identification has been saved in', privkey], c = ['blue', 'cyan'], template = '{} {}')
                ecprint(['Your public key has been save in', pubkey], c = ['blue', 'cyan'], template = '{} {}')
        else: pubkey = self.pubkey

        g.encrypt(self.passwd, pubkey).save(self.db)
        if self.verbose is True: ecprint(['Database saved in', self.db], c=['blue', 'cyan'], template = '{} {}')

    def select(self, service, refresh_db = True):
        #Read and decrypt the file
        if self.verbose : ecprint('Reading database', c='blue')
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)
        lines = ''.join([b.decode('utf-8') for b in g.blocks]).split('\n')[:-1]
        #Search for required service
        ecprint('QUERY MATCH', c = 'blue', template = '{}{}{}'.format(19*'*', '{}', 18*'*'))
        for line in lines[1:]:
            serv, passw = line.split('\t')
            if service == serv: ecprint([serv, passw], c = 'cyan', template = '{} : {}')
        print(48 * '*')

        #Refresh db
        if refresh_db :
            if self.verbose : ecprint('Refreshing database', c = 'blue')
            g.encrypt(self.passwd, self.pubkey).save(self.db)

    def insert(self, service, password = ""):
        if password == "":
            password = PasswdManager.passgen()
            ecprint(['Generated password :', password], c = ['blue', 'cyan'], template = '{} {}')

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
        lines = ''.join([b.decode('utf-8') for b in g.blocks]).split('\n')[:-1]
        #lsit services and passwords
        ecprint('DATABASE', c = 'blue', template = '{}{}{}'.format(20*'*', '{}', 20*'*'))
        if len(lines[1:]) == 0: ecprint('No services stored', c = 'yellow')
        for line in lines[1:]: ecprint(line.split('\t'), c = 'yellow', template = '{} : {}')
        print(48 * '*')

        #Refresh db
        if refresh_db :
            if self.verbose : ecprint('Refreshing database', c = 'blue')
            g.encrypt(self.passwd, self.pubkey).save(self.db)

    def version(self, refresh_db = True):
        if self.verbose : ecprint('Reading database', c='blue')

        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)
        line = g.blocks[0].decode('utf-8').split('\n')[0]
        for v in line.split('\t'): ecprint(v, c = 'cyan')

        if refresh_db :
            if self.verbose : ecprint('Refreshing database', c = 'blue')
            g.encrypt(self.passwd, self.pubkey).save(self.db)

    def changedbpass(self, newpasswd):
        if self.verbose : ecprint('Decrypting database', c='blue')
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)

        if self.verbose : ecprint('Encrypting database with new password', c='blue')
        g.encrypt(newpasswd, self.pubkey).save(self.db)

    def changekey(self, newkey, createRSA, newpassphrase = ""):
        if self.verbose : ecprint('Decrypting database', c='blue')
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)

        if createRSA:
            ecprint('Creating new rsa pair', c = 'blue')
            keyargs = {'dir' : '/'.join(newkey.split('/')[:-1]), 'name' : newkey.split('/')[-1]}
            privkey, pubkey = Giltzarrapo.generateRSApair(newpassphrase, **{k : v for k,v in keyargs.items() if v is not ""})
            if self.verbose is True:
                ecprint(['Your new identification has been saved in', privkey], c = ['blue', 'cyan'], template = '{} {}')
                ecprint(['Your new public key has been save in', pubkey], c = ['blue', 'cyan'], template = '{} {}')
        else:
            ecprint('Using existing pair of keys', c = 'blue')
            pubkey = '{}.pub'.format(newkey)

        if self.verbose : ecprint('Encrypting database with new key', c='blue')
        g.encrypt(self.passw, pubkey).save(self.db)

    def countmatches(self, service, show = True):
        #Read and decrypt the file
        if self.verbose : ecprint('Reading database', c='blue')
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)
        lines = ''.join([b.decode('utf-8') for b in g.blocks]).split('\n')[:-1]
        matches = [l for l in lines[1:] if l.split('\t')[0] == service]
        if len(matches) == 0: ecprint('No query matches for service {}'.format(service), c = 'red')
        else:
            if self.verbose : ecprint([len(matches), 'matches for service', service], c = ['cyan', 'blue', 'cyan'], template = '{} {} {}')
            if show :
                ecprint('QUERY MATCH', c = 'blue', template = '{}{}{}'.format(19*'*', '{}', 18*'*'))
                for i,m in enumerate(matches): ecprint([i] + m.split('\t'), c='cyan', template='{} -> {} : {}')
                print(48 * '*')
        return len(matches)

    def remove(self, service, index = 0):
        #Read and decrypt the file
        g = Giltzarrapo().readEncrypted(self.db).decrypt(self.passwd, self.privkey, self.passphrase)

        #Get the raw payload and the row to delete
        if self.verbose : ecprint('Removing from database', c='blue')
        payload = bytes()
        for b in g.blocks: payload += b
        lines = ''.join([b.decode('utf-8') for b in g.blocks]).split('\n')[:-1]
        if index == '*': removerow = [l.encode('utf-8') for l in lines[1:] if l.split('\t')[0] == service]
        else : removerow = [l for l in lines[1:] if l.split('\t')[0] == service][index].encode('utf-8')

        #Remove those bytes from the payload
        if isinstance(removerow, list):
            while len(removerow) > 0:
                payload = payload[:payload.index(removerow[0])] + payload[payload.index(removerow[0]) + len(removerow[0]) + 1:]
                removerow = removerow[1:]
        else: payload = payload[:payload.index(removerow)] + payload[payload.index(removerow) + len(removerow) + 1:]



        #pull payload to g.blocks
        newbcount = (len(payload) // g.chunkSize)
        if (len(payload) // g.chunkSize) != (len(payload) / g.chunkSize): newbcount += 1
        g.blocks = [payload[g.chunkSize*i:g.chunkSize*(i+1)] for i in range(newbcount)]

        #save modified db
        if self.verbose : ecprint('Saving modified database', c='blue')
        g.encrypt(self.passwd, self.pubkey).save(self.db)

    #change service pass
    #export db
    #import db
