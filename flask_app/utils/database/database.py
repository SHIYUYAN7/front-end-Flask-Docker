import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        
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
                            inst_level['positions'][post_count]['experiences'][expe_count] = {
                                'description' : expe['description'],
                                'end_date'    : expe['end_date'],
                                'hyperlink'   : expe['hyperlink'],
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


