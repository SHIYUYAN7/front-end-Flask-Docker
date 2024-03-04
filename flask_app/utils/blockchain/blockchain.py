from hashlib import sha256
from datetime import datetime
import json
import requests
from flask import request

class Block:
    def __init__(self, index, time_stamp, transactions, previous_hash, work_proof=0):
        self.index = index
        self.time_stamp = time_stamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.work_proof = work_proof

    """ A block is the hash of a string including proof of work"""

    @property 
    def hash(self):

        block_to_hash = str(self.index) + str(self.time_stamp) + str(self.transactions) + str(self.previous_hash) + str(self.work_proof)

        return sha256(block_to_hash.encode()).hexdigest()

class Blockchain:

    def __init__(self, user_wallet, blockchain_wallet, last_chain_index, chain, new_transactions):

        # A block hash will start with a 0 as proof of work
        self.zeros_leading = 1 
        self.new_transactions = new_transactions
        self.chain = chain
        self.user_wallet = user_wallet
        self.blockchain_wallet = blockchain_wallet
        self.last_chain_index = last_chain_index
        # self.generate_genesis_block() # A genesis block is the starting block during initialization 
        

        """A genesis block is the first block in a blockchain, its previous hash would be 0.
        Start with a genesis block by calling Block(0, str(0), [], 0, 0) and appending it to the start of chain""" 
    def generate_genesis_block(self):
        # I am not using this function, I just create a '0' in chain to be genesis block
        
        
        
        """A block is added to the chain in blockchain if the previous hash is valid and the proof of work is valid""" 
    def append_block(self,new_hash):
        return self.chain['chain'] + new_hash
        
        
        
        """First check if there are any pending new blocks, then determine if the transaction came from a valid logged in user with a valid key. 
        A new transaction is only added in a block by first finding a valid proof of work after which the block is appended to the chain. 
        A proof of work will be valid if the given hash starts with 2 leading zeros.  (here Idk, may be jut one leading zeros)
        Flush out new transactions array in the end and return new block """
    def mine_transaction(self):
        # complete code here
        if self.check_transaction_validity():
            if self.check_proof_of_work_valididty():
                date = datetime.now()

                previous_hash = ""
                new_index = self.last_chain_index['chain_index']+1
                if self.last_chain_index['chain_index'] == 1:
                    previous_hash = '*'
                else:
                    previous_hash = '*' + self.chain['chain'].split('*')[-1]
               
                new_block = Block(new_index, date, self.new_transactions, previous_hash, 1)
                block_hash = '*' + new_block.hash

                new_hash = self.append_block(block_hash)
                
                result = {'new_hash':new_hash, 'new_index':new_index, 'date': date, 'previous_hash':previous_hash,'prof_work': 1}
                return result
        return None
                    
        
        """To verify transaction validity, just match the two sets of keys for the user requesting transaction""" 
    def check_transaction_validity(self):  
        # print(self.user_wallet['user_id'],self.user_wallet['token'])
        # check keys and token
        if self.user_wallet['user_id'] == self.blockchain_wallet['user_id'] and self.user_wallet['token'] == self.blockchain_wallet['token']:
            return True
        else:
            return False
        
        
        """A proof of work is valid if the given hash starts with a leading * """
    def check_proof_of_work_valididty(self):
        # print(self.chain)
        # just have the genesis
        if self.chain['chain'] == "*":
            return True
        else:
            chain = self.chain['chain']
            last_chain_withoutstar = chain.split('*')[-1]
            if len(last_chain_withoutstar) == 64:
                return True
        return False

        
        """ To validate entire blockchain excluding the genesis block. A chain is valid if all blocks have valid proof of work"""
    def check_chain_validity(self):
        """complete code here"""
        
