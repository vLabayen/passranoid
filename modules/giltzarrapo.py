#!/usr/bin/python3

#????: Como de asequible es cascar el sha1 para obtener el sha256???
#TODO: Add functionalidad de obtener el bloque en modo fast = false a partir del fichero export_auth
    #Propagar a encrypt y decrypt

import os
import sys
import math
import getopt
from getpass import getuser
from random import randint
from operator import itemgetter
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA, SHA256, SHA512
from Crypto.PublicKey import RSA

class Giltzarrapo:
    def __init__(self, chunkSize = 512):
        self.chunkSize = chunkSize
        self.blocks = []
        self.info = {}
        self.status = None

    @staticmethod
    def generateRSApair(passphrase = "", dir = None, name = "giltza_rsa"):
        if dir != None:
            #Replace ~ for the user's home
            if '~' in dir : dir = '/home/{}/{}'.format(getuser(), dir[len(dir) - ''.join(list(reversed(dir))).index('~') + 1:])
            if dir[-1] is '/': dir = dir[:-1] #ensure no extra / at the end

            if not os.path.exists(dir) : raise ValueError('No such directory : {}'.format(dir))
            file_template = '{}/{}'.format(dir, name)
        else : file_template = '{}/{}'.format(dir, os.getcwd())

        privKey = file_template
        pubKey = '{}.pub'.format(file_template)

        key = RSA.generate(4096, Random.new().read)
        try :
            with open(privKey, 'wb') as priv, open(pubKey, 'wb') as pub:
                priv.write(key.exportKey("PEM", passphrase = passphrase))
                pub.write(key.publickey().exportKey("PEM"))
        except PermissionError: raise PermissionError('Write permision denied at : {}'.format(file_template))
        return privKey, pubKey

    @staticmethod
    def entropy(string):
        """Calculates the Shannon entropy of a string"""

        # get probability of chars in string
        prob = [ float(string.count(c)) / len(string) for c in dict.fromkeys(list(string)) ]

        return (- sum([ p * math.log(p) / math.log(2.0) for p in prob ]))

    def selectBlock(self, tryLimit = 5):
        try_blocks = [randint(0, len(self.blocks) - 1) for _ in range(tryLimit)]
        blocks_entropy = { block_index : Giltzarrapo.entropy(self.blocks[block_index].hex()) for block_index in try_blocks}
        selected_block = max(blocks_entropy.items(), key = itemgetter(1))[0]

        return selected_block

    def verifySymetricBlock(self, selected_block, pubkey):
        if self.status is None : raise TypeError('Must have a readed file in memory')
        if not os.path.isfile(pubkey): raise ValueError('No such file or directory : {}'.format(pubkey))

        try : PUBkey = RSA.importKey(open(pubkey, "rb").read())
        except ValueError: raise KeyError('Wrong key format')
        except PermissionError: raise PermissionError('Read permission denied : {}'.format(pubkey))
        if PUBkey.has_private(): raise KeyError('Wrong key format')

        if type(selected_block) != int:
            raise ValueError('The selected block must be an int')
        if selected_block > len(self.blocks) - 1 or selected_block < 0:
            raise ValueError('The selected block ({}) must satisfy :\n\t{}\n\t{}'.format(selected_block,
                'selected block <= {}'.format(len(self.blocks) - 1),
                'selected block >= 0'
            ))

        if selected_block == len(self.blocks) - 1:
            block_size = len(self.blocks[-1])
            b = self.blocks[-1] + os.urandom(self.chunkSize - block_size)
        else : b = self.blocks[selected_block]

        try: PUBkey.encrypt(b, 32)
        except : return False;
        return True;
         
    def findBlock(self, passwd, privkey, passphrase):
        if not os.path.isfile(privkey): raise ValueError('No such file or directory : {}'.format(privkey))

        try : PRIVkey = RSA.importKey(open(privkey, "rb").read(), passphrase = passphrase)
        except ValueError: raise ValueError('Wrong or required passphrase')
        except PermissionError: raise PermissionError('Read permission denied : {}'.format(privkey))
        if not PRIVkey.has_private(): raise KeyError('Wrong key format')

        for i,b in enumerate(self.blocks):
            if self.info['fast'] :
                passwd_hash = SHA512.new(bytes('{}{}{}'.format(self.info['challenge'].hex(), i, passwd), encoding='utf-8')).digest()
                if passwd_hash != self.info['auth']: continue

            try : block_hash = SHA256.new(PRIVkey.decrypt(b) + bytes(passwd, encoding = 'utf-8')).digest()
            except : continue

            signature = SHA.new(block_hash).digest()
            if signature == self.info['challenge']: return i

        raise ValueError('The symetric block could not be found. It may be caused by a wrong password and/or privkey')

    def readPlain(self, infile):
        if not os.path.isfile(infile): raise ValueError('No such file or directory : {}'.format(infile))

        blocks = []
        try :
            with open(infile, 'rb') as inf:
                bytes_read = inf.read(self.chunkSize)
                while bytes_read:
                    blocks.append(bytes_read)
                    bytes_read = inf.read(self.chunkSize)
        except PermissionError: raise PermissionError('Read permission denied : {}'.format(infile))

        self.blocks = blocks
        self.status = "plain"
        return self

    def encrypt(self, passwd, pubkey, selected_block = None, fast = True, try_max = 10):
        try:
            if try_max > 0: self._encrypt(passwd, pubkey, selected_block, fast)
        except (KeyError, PermissionError) as e: raise e
        except ValueError:
            if selected_block == None: self.encrypt(passwd, pubkey, selected_block, fast, try_max - 1)
            if self.status is not 'encrypted': raise ValueError('Error in RSA encryption for block {}'.format(selected_block))

        return self

    def _encrypt(self, passwd, pubkey, selected_block = None, fast = True):
        if not os.path.isfile(pubkey): raise ValueError('No such file or directory : {}'.format(pubkey))

        try : PUBkey = RSA.importKey(open(pubkey, "rb").read())
        except ValueError: raise KeyError('Wrong key format')
        except PermissionError: raise PermissionError('Read permission denied : {}'.format(pubkey))
        if PUBkey.has_private(): raise KeyError('Wrong key format')

        #Select a valid block as symetric key
        if selected_block == None: selected_block = self.selectBlock()
        else:
            if type(selected_block) != int:
                raise ValueError('The selected block must be an int')
            if selected_block > len(self.blocks) - 1 or selected_block < 0:
                raise ValueError('The selected block ({}) must satisfy :\n\t{}\n\t{}'.format(selected_block,
                    'selected block <= {}'.format(len(self.blocks) - 1),
                    'selected block >= 0'
                ))

        #Padding
        block_size = len(self.blocks[-1])
        self.blocks[-1] = self.blocks[-1] + os.urandom(self.chunkSize - block_size)

        #Encrypt the file
        hash_sha = SHA256.new(self.blocks[selected_block] + bytes(passwd, encoding = 'utf-8')).digest()
        hash_sha_sha = SHA.new(hash_sha).digest()
        encryptor = AES.new(hash_sha, AES.MODE_ECB, "")

        #Store the info
        self.info['fast'] = fast
        self.info['padding'] = self.chunkSize - block_size
        self.info['challenge'] = hash_sha_sha
        self.info['auth'] = SHA512.new(bytes('{}{}{}'.format(hash_sha_sha.hex(), selected_block, passwd), encoding='utf-8')).digest()

        #Encrypt the file
        for i,b in enumerate(self.blocks):
            self.blocks[i] = PUBkey.encrypt(b, 32)[0] if (i == selected_block) else encryptor.encrypt(b)

        self.status = "encrypted"
        return self

    def readEncrypted(self, infile):
        if not os.path.isfile(infile): raise ValueError('No such file or directory : {}'.format(infile))

        blocks = []
        info = {}
        try :
            with open(infile, 'rb') as inf:
                info['fast'] = bool.from_bytes(inf.read(1), byteorder='little')
                info['padding'] = int.from_bytes(inf.read(2), byteorder='little')
                info['challenge'] = inf.read(20)
                if info['fast'] : info['auth'] = inf.read(64)

                bytes_read = inf.read(self.chunkSize)
                while bytes_read:
                    blocks.append(bytes_read)
                    bytes_read = inf.read(self.chunkSize)
        except PermissionError: raise PermissionError('Read permission denied : {}'.format(infile))

        self.blocks = blocks
        self.info = info
        self.status = "encrypted"
        return self

    def decrypt(self, passwd, privkey, passphrase, selected_block = None):
        if not os.path.isfile(privkey): raise ValueError('No such file or directory : {}'.format(privkey))

        try : PRIVkey = RSA.importKey(open(privkey, "rb").read(), passphrase = passphrase)
        except ValueError: raise ValueError('Wrong or required passphrase')
        except PermissionError: raise PermissionError('Read permission denied : {}'.format(privkey))
        if not PRIVkey.has_private(): raise KeyError('Wrong key format')

        #Found and check the selected block
        if selected_block == None:
            selected_block = self.findBlock(passwd, privkey, passphrase)
            block_hash = SHA256.new(PRIVkey.decrypt(self.blocks[selected_block]) + bytes(passwd, encoding = 'utf-8')).digest()
        else:
            if type(selected_block) != int:
                raise ValueError('The selected block must be an int')
            if selected_block > len(self.blocks) - 1 or selected_block < 0:
                raise ValueError('The selected block ({}) must satisfy :\n\t{}\n\t{}'.format(selected_block,
                    'selected block < {}'.format(len(self.blocks)),
                    'selected block >= 0'
                ))

            try : block_hash = SHA256.new(PRIVkey.decrypt(self.blocks[selected_block]) + bytes(passwd, encoding = 'utf-8')).digest()
            except : raise ValueError('Can not decrypt with {} as selected block'.format(selected_block))

            signature = SHA.new(block_hash).digest()
            if signature != self.info['challenge']: raise ValueError('Wrong selected block or wrong password')

        encryptor = AES.new(block_hash)

        #Decrypt the file
        for i,b in enumerate(self.blocks):
            mode = PRIVkey if (i == selected_block) else encryptor
            self.blocks[i] = mode.decrypt(b)[:self.chunkSize - self.info['padding']] if (i == (len(self.blocks) - 1)) else mode.decrypt(b)

        self.status = "plain"
        return self

    def save(self, outfile, export_auth = None):
        if self.status == None: raise TypeError('There is no readed data to save')

        try :
            with open(outfile, 'wb') as outf:
                if self.status == 'encrypted':
                    #write whether or not the fast mode is enabled
                    outf.write(self.info['fast'].to_bytes(1, byteorder='little'))
                    #write 2 bytes for the last block padding
                    outf.write(self.info['padding'].to_bytes(2, byteorder='little'))
                    #write the 20bytes of the SHA1
                    outf.write(self.info['challenge'])
                    #write the 64 bytes of the sha512 of the salted password if fast is enabled
                    if self.info['fast'] : outf.write(self.info['auth'])

                for i,b in enumerate(self.blocks): outf.write(b)
        except PermissionError : raise PermissionError('Write permission denied : {}'.format(outfile))

        try :
            if export_auth != None:
                with open(export_auth, 'wb') as authf: authf.write(self.info['auth'])
        except PermissionError : raise PermissionError('Write permission denied : {}'.format(export_auth))

    def clear(self):
        self.blocks = []
        self.info = {}
        self.status = None
