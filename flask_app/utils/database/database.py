import mysql.connector
import glob
import json
import csv
from io import StringIO,BytesIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow
from datetime import datetime

from PIL import Image
import numpy as np
# from js import Blob

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users', 'userswallet', 'blockchainwallet', 'images', 'blockchain', 'transactions']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id

    def getResumeData(self):

        # Pulls data from the database
        query_inst = "SELECT * FROM institutions"
        query_posi = "SELECT * FROM positions"
        query_expe = "SELECT * FROM experiences"
        query_skill = "SELECT * FROM skills"
        
        institutions = self.query(query_inst)
        positions = self.query(query_posi)
        experiences = self.query(query_expe)
        skills = self.query(query_skill)

        result = {}

        # institutions
        inst_count = 0
        for inst in institutions:
            inst_count +=1
            inst_level = {
                'address'    :  inst['address'],
                'city'       :  inst['city'],
                'state'      :  inst['state'],
                'type'       :  inst['type'],
                'department' :  inst['department'],
                'name'       :  inst['name'],
                'positions'  : {}
            }

            # positions
            post_count = 0
            for posi in positions:
                #  find a match position
                if inst['inst_id'] == posi['inst_id']:
                    post_count += 1
                    inst_level['positions'][post_count] = {
                        'end_date'        : posi['end_date'],
                        'responsibilities': posi['responsibilities'],
                        'start_date'      : posi['start_date'],
                        'title'           : posi['title'],
                        'experiences': {}
                    }


                    # experiences
                    expe_count = 0
                    for expe in experiences:
                        #  find a match position
                        if expe['position_id'] == posi['position_id']:
                            expe_count += 1
                            link = None
                            if expe['hyperlink'] != 'NULL':
                                link = expe['hyperlink']
                            inst_level['positions'][post_count]['experiences'][expe_count] = {
                                'description' : expe['description'],
                                'end_date'    : expe['end_date'],
                                'hyperlink'   : link,
                                'name'        : expe['name'],
                                'skills'      : {},
                                'start_date'  : expe['start_date']
                            }


                            # skills
                            skill_count = 0
                            for sk in skills:
                                #  find a match position
                                if sk['experience_id'] == expe['experience_id']:
                                    skill_count +=1
                                    inst_level['positions'][post_count]['experiences'][expe_count]['skills'][skill_count] = {
                                        'name'        : sk['name'],
                                        'skill_level' : sk['skill_level']
                                    }

            result[inst_count] = inst_level

        return result
    
    def updateFeedback(self,data):

        # update the new comment
        update = "INSERT INTO feedback ( name, email, comment) VALUES (%s,%s,%s)"
        par_tuple = tuple(data)
        self.query(update,par_tuple)

        # grasp all comments
        select_feedback = "SELECT * FROM feedback"
        rows = self.query(select_feedback)

        result = {}
        for row in rows:
            result[row['comment_id']] = [row['name'],row['comment']]

        return result
    

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        
        checkExist = "SELECT email FROM users WHERE email = '" + email + "'"
        result = self.query(checkExist)

        if len(result) == 0:
            insert = "INSERT INTO users ( role, email, password ) VALUES (%s,%s,%s)"
            par_tuple = (role,email,self.onewayEncrypt(password))
            self.query(insert,par_tuple)

            # create personal wallet
            token = np.random.randint(400,1000)
            key = str(np.random.randint(1000000,1900000))+ email[:4]

            # get userid
            user_id = self.gerUserId(email)

            # insert wallet
            insert_wallet = "INSERT INTO userswallet ( user_id, user_key, token ) VALUES (%s,%s,%s)"
            wallet_tuple = (int(user_id), key, token)
            self.query(insert_wallet, wallet_tuple)

            # insert blockchain wallet
            insert_blockchainwallet = "INSERT INTO blockchainwallet ( user_id, user_key, token ) VALUES (%s,%s,%s)"
            self.query(insert_blockchainwallet, wallet_tuple)

            # test
            # test = "SELECT * FROM userswallet"
            # tes = self.query(test)
            # print(tes)
            # test2 = "SELECT * FROM blockchainwallet"
            # tes2 = self.query(test2)
            # print(tes2)

            return {'success': 1}
        else:
            return {'fail': 0}

    def authenticate(self, email='me@email.com', password='password'):

        checkExist = "SELECT email FROM users WHERE email = '" + email + "' and password = '" + self.onewayEncrypt(password) + "'" 
        result = self.query(checkExist)
        if len(result)== 1:
            return {'success': 1}
        else:
            return {'fail': 0}


    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message

    def getRole(self,email):
        checkExist = "SELECT role FROM users WHERE email = '" + email + "'"
        result = self.query(checkExist)
        return result

    def gerUserId(self,email):
        # get userid
        getUserId = "SELECT user_id FROM users WHERE email = '" + email + "'"
        res = self.query(getUserId)  
        user_id = res[0]['user_id']
        return user_id      
    
    def getUserWalletInfoByEmail(self,email):
        user_id = self.gerUserId(email)
        qurey = "SELECT * FROM userswallet WHERE user_id = " + str(user_id) 
        res = self.query(qurey) 
        return res
    
    def getUserWalletInfoByUserId(self,user_id):
        qurey = "SELECT * FROM userswallet WHERE user_id = " + str(user_id) 
        res = self.query(qurey) 
        return res
    
    def getBlockchainWalletInfoByUserId(self,user_id):
        qurey = "SELECT * FROM blockchainwallet WHERE user_id = " + str(user_id) 
        res = self.query(qurey) 
        return res
    
    def getUserToken(self,user_id):
        token_query = "SELECT * FROM userswallet WHERE user_id = " + str(user_id) 
        token = self.query(token_query)
        return token[0]['token']
    
    def getUserEmail(self,user_id):
        qurey = "SELECT email FROM users WHERE user_id = " + str(user_id) 
        res = self.query(qurey) 
        return res

#######################################################################################
# IMAGES RELATED
#######################################################################################
    def createImage(self,email,description,token):

        # the dimensions of the image
        width = 384
        height = 384
        
        colorR1 = np.random.randint(0,128)
        colorR2 = np.random.randint(130,255)

        # density of img
        step = np.random.randint(20,100)

        # create ramdom pixel by numpy
        pixels = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(0, height, step):
            for j in range(0, width, step):
                pixels[i:i+step, j:j+step] = np.random.randint(colorR1, colorR2, (1, 1, 3), dtype=np.uint8)

        img = Image.fromarray(pixels)
        
        # save to database and get the local path
        img_path,date_string = self.saveImageSQL(email, description, token)
        #  save local
        img.save(img_path)

        return {'success': 1,'description':description,'token':token,'image_id':int(date_string)}
    
    def uploadImage(self,file,email,description,token):
        # open the file
        img = Image.open(file)
    
        # save to database and get the local path
        img_path,date_string = self.saveImageSQL(email, description, token)
        #  save local
        img.save(img_path)

        return {'success': 1,'description':description,'token':token,'image_id':int(date_string)}
    
    def saveImageSQL(self,email,description,token):
        # get userid
        user_id = self.gerUserId(email)
        
        # get current time
        now = datetime.now()
        date_string = now.strftime('%H%M%S')

        # insert image
        insert_image = "INSERT INTO images (image_id, owner, token, description ) VALUES (%s,%s,%s,%s)"
        image_tuple = (int(date_string), int(user_id), token, description )
        self.query(insert_image, image_tuple)

        # save image with id called timestamp
        img_path = 'flask_app/static/NFTimages/'+ str(int(date_string)) +'.png'

        self.createGensisBlockChain(int(date_string),now)

        return img_path,date_string
    
    def createGensisBlockChain(self,image_id,date):
        # insert chain
        insert_chain = "INSERT INTO blockchain (image_id,chain) VALUES (%s,%s)"
        chain_tuple = (image_id, '*')
        self.query(insert_chain, chain_tuple)

        # insert block
        insert_block = "INSERT INTO transactions (chain_index, timestamp, cost, seller_id, buyer_id, current_owner, image_id, previous_hash, workproof) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        block_tuple = (1, date, 0, "0", "0", "0", image_id, "0", 0)
        self.query(insert_block, block_tuple)

        # search = "SELECT * FROM transactions"
        # print(self.query(search))
        return {'success': 1}

    def getDescriptionByImageID(self,image_id):
        search = "SELECT description FROM images WHERE image_id = " + str(image_id)
        res = self.query(search) 
        return res[0]

    def getOwnImages(self,email):
        # get userid
        user_id = self.gerUserId(email)

        search = "SELECT * FROM images WHERE owner = " + str(user_id) 
        images = self.query(search)
        # let the image_id to str
        for image in images:
            image['image_id'] = str(image['image_id'])
        return images   
    
    def getAllImages(self,email):
        # get userid
        user_id = self.gerUserId(email)

        # the users see the images they are selling/owning on the buyer page
        search = "SELECT * FROM images WHERE owner != " + str(user_id)
        images = self.query(search)
        # let the image_id to str
        for image in images:
            image['image_id'] = str(image['image_id'])
        return images  
    
    def editImage(self,email,description,token,image_id):
        # get userid
        user_id = self.gerUserId(email)

        update = ''
        update_tuple = ()

        if description != 'unchange' and token != 'unchange':
            update =  "UPDATE images SET description = %s, token = %s WHERE owner = %s AND image_id = %s"
            update_tuple = (description, token, user_id, image_id)
        elif token != 'unchange':
            update =  "UPDATE images SET token = %s WHERE owner = %s AND image_id = %s"
            update_tuple = (token, user_id, image_id)
        elif description != 'unchange':
            update =  "UPDATE images SET description = %s WHERE owner = %s AND image_id = %s"
            update_tuple = (description, user_id, image_id)

        # print(self.getOwnImages(email))

        self.query(update,update_tuple)
        # print('after change')
        # print(self.getOwnImages(email))
        return {'success': 1}
    
    def getTransactionNeed(self, email, image_id):
        
        user_id = self.gerUserId(email)

        # get image info
        image_query = "SELECT * FROM images WHERE image_id = " + str(image_id) 
        images = self.query(image_query)
        new_transactions = [images[0]['token'],images[0]['owner'],user_id,user_id,image_id]

        # get user info (key and token)
        user_wallet = self.getUserWalletInfoByUserId(user_id);
        blockchain_wallet = self.getBlockchainWalletInfoByUserId(user_id)
        
        # last block
        recent_query = "SELECT chain_index FROM transactions WHERE image_id = " + str(image_id) + " ORDER BY chain_index DESC LIMIT 1"
        last_chain_index = self.query(recent_query)

        # last chain
        chain_query = "SELECT * FROM blockchain WHERE image_id = " + str(image_id) 
        chain = self.query(chain_query)


        # print(user_wallet[0],blockchain_wallet[0])
        # print(last_chain_index[0])
        # print(chain[0])
        
        return user_wallet[0],blockchain_wallet[0],last_chain_index[0],chain[-1],new_transactions

    
    def validTokenEnough(self,email,image_token):
        user_id = self.gerUserId(email)
        user_token = self.getUserToken(user_id)
        if int(user_token) - int(image_token) > 0:
            return True
        else:
            return False

    def finishBought(self,infos,new_transactions):
        # new_transactions: cost,seller,buyer,current_owner,image_id

        # buyer
        buyer_wallet = self.getUserWalletInfoByUserId(new_transactions[2])
        buyer_token = buyer_wallet[0]['token']
        left_token = buyer_token - new_transactions[0]

        # seller
        seller_wallet = self.getUserWalletInfoByUserId(new_transactions[1])
        seller_token = seller_wallet[0]['token']
        add_token = seller_token + new_transactions[0]

        # update two wallet
        buyer_userwallet = "UPDATE userswallet SET token = %s WHERE user_id = %s"
        buyer_userwallet_tuple = (left_token, new_transactions[2])
        self.query(buyer_userwallet, buyer_userwallet_tuple)

        seller_userwallet = "UPDATE userswallet SET token = %s WHERE user_id = %s"
        seller_userwallet_tuple = (add_token, new_transactions[1])
        self.query(seller_userwallet, seller_userwallet_tuple)
        # print(self.query("SELECT * FROM userswallet"))

        buyer_blockchainwallet = "UPDATE blockchainwallet SET token = %s WHERE user_id = %s"
        buyer_blockchainwallet_tuple = (left_token, new_transactions[2])
        self.query(buyer_blockchainwallet, buyer_blockchainwallet_tuple)

        seller_blockchainwallet = "UPDATE blockchainwallet SET token = %s WHERE user_id = %s"
        seller_blockchainwallet_tuple = (add_token, new_transactions[1])
        self.query(seller_blockchainwallet, seller_blockchainwallet_tuple)
        # print(self.query("SELECT * FROM blockchainwallet"))

        # update image
        # print(self.query("SELECT * FROM images"))
        update_image =  "UPDATE images SET owner = %s WHERE image_id = %s"
        update_image_tuple = (new_transactions[2], new_transactions[4])
        self.query(update_image, update_image_tuple)
        # print(self.query("SELECT * FROM images"))

        # insert transaction
        insert_block = "INSERT INTO transactions (chain_index, timestamp, cost, seller_id, buyer_id, current_owner, image_id, previous_hash, workproof) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        block_tuple = (infos['new_index'], infos['date'], new_transactions[0], new_transactions[1], new_transactions[2], new_transactions[2], new_transactions[4], infos['previous_hash'], 1)
        self.query(insert_block, block_tuple)
        print(self.query("SELECT * FROM transactions"))

        # update blockchain
        insert_chain = "UPDATE blockchain SET chain = %s WHERE image_id = %s"
        chain_tuple = (infos['new_hash'], new_transactions[4])
        self.query(insert_chain, chain_tuple)
        # print(self.query("SELECT * FROM blockchain"))

        return {'success': 1}
    
    def getAdminInfo(self,):
        all_transaction = self.query("SELECT chain_index, timestamp, cost, seller_id, buyer_id, current_owner, image_id FROM transactions")
        all_blockchain = self.query("SELECT image_id, chain FROM blockchain")

        # manage transaction
        for transaction in all_transaction:
            if transaction['chain_index'] != 1:

                # save image description
                image_description = self.getDescriptionByImageID(transaction['image_id'])
                transaction['image_description'] = image_description['description']

                # change time format
                timestamp = transaction['timestamp']
                transaction['timestamp'] = timestamp.strftime("%Y-%m-%d %I:%M:%S%p")
                
                # change seller_id, buyer_id, current_owner to email
                seller_id = transaction['seller_id']
                buyer_id = transaction['buyer_id']

                seller = self.getUserEmail(seller_id)
                buyer = self.getUserEmail(buyer_id)

                transaction['seller_id'] = seller[0]['email']
                transaction['buyer_id'] = buyer[0]['email']
                transaction['current_owner'] = buyer[0]['email']
        
        for chain in all_blockchain:
            # save image description
            image_description = self.getDescriptionByImageID(chain['image_id'])
            chain['image_description'] = image_description['description']

        return all_transaction, all_blockchain
        
