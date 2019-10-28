import os
from random import randint
from printer import cprint, cprepare, ctable
from giltzarrapo import Giltzarrapo

class PasswdManager:
    verbose = False

    @staticmethod
    def passgen(length = 20, alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890!¡()?¿{}[]<>|@#$%&/=+*-_.:;,'):
        if alphabet == '': return PasswdManager.passgen(length = length)
        else : return ''.join([alphabet[randint(0, len(alphabet) - 1)] for _ in range(length)])

    @staticmethod
    def create(dbname, passwd, passphrase, databases_path, keys_path):
        if PasswdManager.verbose: print(cprepare('Creating', color = 'blue'), cprepare(dbname, color = 'lblue'), cprepare('database', color = 'blue'))
        g = Giltzarrapo()
        InternalPasswdManager.append(g, 'passranoid_database:v1.1\tpassranoid_interface:v1.2\tpassranoid_config:v1\n')
        g.status = 'plain'

        if PasswdManager.verbose: cprint('Generating rsa key pair', color = 'blue')
        privkey, pubkey = Giltzarrapo.generateRSApair(passphrase, dir = keys_path, name = dbname)
        if PasswdManager.verbose: print(cprepare('Keys saved at :\n  - Privkey :', color = 'blue'), cprepare(privkey, color = 'lblue'), cprepare('\n  - Pubkey :', color = 'blue'), cprepare(pubkey, color = 'lblue'))

        if PasswdManager.verbose: print(cprepare('Saving database at :', color = 'blue'), cprepare('{}/{}'.format(databases_path, dbname), color = 'lblue'))
        g.encrypt(passwd, pubkey).save('{}/{}'.format(databases_path, dbname))

    @staticmethod
    def insert(conf, service, user, spasswd, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Inserting new row', color = 'blue')
        if spasswd == '': spasswd = PasswdManager.passgen()
        InternalPasswdManager.append(g, '{}\t{}\t{}\n'.format(service, user, spasswd))
        if PasswdManager.verbose: ctable(header = ['service', 'user', 'password'], data = [[service, user, spasswd]], header_color = 'blue', rows_color = 'lblue')

        if PasswdManager.verbose: cprint('Saving modified database', color = 'blue')
        g.encrypt(passwd, conf['pubkey']).save(conf['dbfile'])

    @staticmethod
    def list(conf, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Fetching rows', color = 'blue')
        lines = InternalPasswdManager.getlines(g, '*')

        if PasswdManager.verbose: cprint('Refreshing database', color = 'blue')
        g.encrypt(passwd, conf['pubkey']).save(conf['dbfile'])
        return lines

    @staticmethod
    def select(conf, service, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Fetching matching rows', color = 'blue')
        lines = InternalPasswdManager.getlines(g, service)

        if PasswdManager.verbose: cprint('Refreshing database', color = 'blue')
        g.encrypt(passwd, conf['pubkey']).save(conf['dbfile'])
        return lines

    @staticmethod
    def remove(conf, index, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Removing matching rows', color = 'blue')
        if index == '*' : removerows = [l[1].encode('utf-8') for l in InternalPasswdManager.getlines(g, '*')]
        else :
            try : removerows = InternalPasswdManager.getlines(g, '*')[index][1].encode('utf-8')
            except IndexError: return False
        InternalPasswdManager.remove(g, removerows)

        if PasswdManager.verbose: cprint('Saving modified database', color = 'blue')
        g.encrypt(passwd, conf['pubkey']).save(conf['dbfile'])
        return True

    @staticmethod
    def version(conf, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Fetching database version', color = 'blue')
        version = InternalPasswdManager.getversion(g)

        if PasswdManager.verbose: cprint('Refreshing database', color = 'blue')
        g.encrypt(passwd, conf['pubkey']).save(conf['dbfile'])
        return version

    @staticmethod
    def changedbpass(conf, newpasswd, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Encrypting database with the new password', color = 'blue')
        g.encrypt(newpasswd, conf['pubkey']).save(conf['dbfile'])

    @staticmethod
    def changedbkey(conf, newpassphrase, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Generating rsa key pair', color = 'blue')
        keys_path, keyname = '/'.join(conf['privkey'].split('/')[:-1]), conf['privkey'].split('/')[-1]
        os.rename(conf['privkey'], '{}/.old.{}'.format(keys_path, keyname))
        os.rename(conf['pubkey'], '{}/.old.{}.pub'.format(keys_path, keyname))
        privkey, pubkey = Giltzarrapo.generateRSApair(newpassphrase, dir = keys_path, name = keyname)
        if PasswdManager.verbose: print(cprepare('Old keys moved to :\n  - Privkey :', color = 'blue'), cprepare('{}/.old.{}'.format(keys_path, keyname), color = 'lblue'), cprepare('\n  - Pubkey :', color = 'blue'), cprepare('{}/.old.{}.pub'.format(keys_path, keyname), color = 'lblue'))
        if PasswdManager.verbose: print(cprepare('New keys saved at :\n  - Privkey :', color = 'blue'), cprepare(privkey, color = 'lblue'), cprepare('\n  - Pubkey :', color = 'blue'), cprepare(pubkey, color = 'lblue'))

        if PasswdManager.verbose: cprint('Encrypting database with the new key pair', color = 'blue')
        g.encrypt(passwd, pubkey).save(conf['dbfile'])

    @staticmethod
    def exportdb(conf, dbfile, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: cprint('Fetching rows', color = 'blue')
        header = '\t'.join(['service', 'user', 'password'])
        lines = [l for i,l in InternalPasswdManager.getlines(g, '*')]
        if len(lines) == 0: return False

        if PasswdManager.verbose: print(cprepare('Saving plain database rows at :', color = 'blue'), cprepare(dbfile, color = 'lblue'))
        InternalPasswdManager.savefile(header = header, lines = lines, file = dbfile)
        return True

    @staticmethod
    def importdb(conf, dbfile, passwd, passphrase):
        if PasswdManager.verbose: cprint('Reading and decrypting database', color = 'blue')
        g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)

        if PasswdManager.verbose: print(cprepare('Reading plain exported file :', color = 'blue'), cprepare(dbfile, color = 'lblue'))
        content = InternalPasswdManager.readfile(dbfile)
        header_fields = ['service', 'user', 'password']
        old_header, lines = content[0].split('\t'), [l.split('\t') for l in content[1:]]
        line_template = '{}\n'.format('\t'.join([('{}' if h in header_fields else ' ') for h in old_header]))

        if PasswdManager.verbose: print(cprepare('Inserting rows in', color = 'blue'), cprepare(conf['dbfile'].split('/')[-1], color = 'lblue'), cprepare('database', color = 'blue'))
        for l in lines: InternalPasswdManager.append(g, line_template.format(*l))

        if PasswdManager.verbose: cprint('Saving modified database', color = 'blue')
        g.encrypt(passwd,conf['pubkey']).save(conf['dbfile'])

    @staticmethod
    def verifyauth(conf, passwd, passphrase):
        if PasswdManager.verbose: cprint('Verifying database credentials', color = 'blue')
        try :
            g = Giltzarrapo().readEncrypted(conf['dbfile']).decrypt(passwd, conf['privkey'], passphrase)
            g.encrypt(passwd, conf['pubkey']).save(conf['dbfile'])
        except : return False
        if PasswdManager.verbose: cprint('Successfully verification', color = 'green')
        return True

class InternalPasswdManager:

    @staticmethod
    def append(g, newline):
        newline = bytes(newline, encoding = 'utf-8')

        if len(g.blocks) > 0:
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

    @staticmethod
    def getlines(g, service):
        lines = ''.join([b.decode('utf-8') for b in g.blocks]).split('\n')[1:-1] #Exclude last empty line and version line
        lines = [(i,l) for i,l in enumerate(lines)]
        if service != '*': lines = [l for l in lines if l[1].split('\t')[0] == service]
        return lines

    @staticmethod
    def getversion(g):
        return ''.join([b.decode('utf-8') for b in g.blocks]).split('\n')[0]

    @staticmethod
    def remove(g, rlines):
        payload = bytes()
        for b in g.blocks: payload += b

        #Remove bytes from the payload
        if isinstance(rlines, list):
            for r in rlines:
                payload = payload[:payload.index(r)] + payload[payload.index(r) + len(r) + 1:]
        else : payload = payload[:payload.index(rlines)] + payload[payload.index(rlines) + len(rlines) + 1:]

        #pull payload to g.blocks
        newbcount = (len(payload) // g.chunkSize)
        if (len(payload) // g.chunkSize) != (len(payload) / g.chunkSize): newbcount += 1
        g.blocks = [payload[g.chunkSize*i:g.chunkSize*(i+1)] for i in range(newbcount)]

    @staticmethod
    def savefile(header, lines, file):
        with open(file, 'w') as f:
            f.write('{}\n'.format(header))
            for l in lines: f.write('{}\n'.format(l))

    @staticmethod
    def readfile(file):
        with open(file, 'r') as f:
            lines = [l.split('\n')[0] for l in f]
        return lines
