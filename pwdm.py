import hashlib
import base64
from cryptography.fernet import Fernet
import os
import sys
import sqlite3
import random
from datetime import datetime

def getsecretkey(master_pwd):
    '''generates a 640 character long secret key using various combinations of master password and hashing them with sha512'''
    var1, var2, var3, var4, var5= '','','','',''
    for i in range(len(master_pwd)):
        var1+=master_pwd[i]
        var2+=master_pwd[i].upper()
        var3+=master_pwd[i].lower()
        if i%2==0:
            var4+=master_pwd[i].upper()
        else:
            var4+=master_pwd[i].lower()
        var5+=str(i)+master_pwd[i]

    var1= var1+var5+var4
    var2= var2+ var1
    var3= var1+ var3
    var4= var4+var5+var4
    var5=var5+var1
    varlist=[var1, var2, var3, var4, var5]

    secret_key=''
    for i in range(len(varlist)):
        temp_key=varlist[i]
        for j in range(len(var1)):
            temp_key=hashlib.sha512(temp_key.encode()).hexdigest()
        secret_key+=temp_key
    return secret_key

def storepassword(secret_key, master_pwd):
    '''Stores  password by encrypting them using the fernet key which is generated as a combination of secret key and master password.'''
    company= input('Enter company name (like Google, Facebook, Mail, etc..): ')
    passkey=input('Enter password to store: ')
    passkey= passkey.encode()
    date= datetime.now()
    a,b,c,d=random.randint(64,576),random.randint(64,576),random.randint(64,576),random.randint(64,576)
    choosen=str(a)+','+str(b)+','+str(c)+','+str(d)
    cryp_key=secret_key[a:a+8]+master_pwd+secret_key[b:b+8]+master_pwd+secret_key[c:c+8]+master_pwd+secret_key[d:d+8]+ master_pwd
    cryp_key= cryp_key[0:32]
    cryp_key= base64.urlsafe_b64encode((cryp_key).encode())
    suite=Fernet(cryp_key)
    passkey= suite.encrypt(passkey)
    with conn:
        curr.execute(''' INSERT INTO  pwdb_table (choosen,company,date,key) VALUES(?,?,?,?)''', (choosen, company,date, passkey))
    print('Successfully encrypted password of: '+ company)

def retordel(value, secret_key, master_pwd):
    '''Displays decrypted value of password from the database and can also delete the encrypted password records in the database.'''
    print('_'*85)
    print('')
    curr.execute("SELECT id, choosen,company,date,key FROM pwdb_table")
    passwithid = curr.fetchall()
    idnames =[]
    for passs in passwithid:
        idnames.append(passs[0])

    for ids in passwithid:
        print(ids[0], ids[2], ids[3])
    print('_'*85)
    if value==2:
        print('Enter ID no. of companies (seperated by comma) to retrieve:')
    elif value == 3:
        print('Enter ID no. of companies (seperated by comma) to delete:')

    inp = input()
    inp = inp.split(',')

    for num in inp:
        try:
            int(num)
        except Exception as e:
            print(e, 'Enter integer values seperated by comma.')
            break

        if int(num) in idnames:
            reqdpass = passwithid[idnames.index(int(num))][1]
            if value == 2:
                reqdpass= reqdpass.split(',')
                a,b,c,d= int(reqdpass[0]), int(reqdpass[1]),int(reqdpass[2]),int(reqdpass[3])
                cryp_key=secret_key[a:a+8]+master_pwd+secret_key[b:b+8]+master_pwd+secret_key[c:c+8]+master_pwd+secret_key[d:d+8]+ master_pwd
                cryp_key= cryp_key[0:32]
                cryp_key= base64.urlsafe_b64encode((cryp_key).encode())
                suite=Fernet(cryp_key)
                curr.execute("SELECT company, key FROM pwdb_table WHERE id = :id", {'id':num})
                dataret = curr.fetchone()
                passenc= dataret[1]
                comp= dataret[0]
                try:
                    repass= suite.decrypt(passenc)
                    print('Password of ' + comp+ ' (ID: '+ str(num)+ ')' ' is:')
                    print(repass.decode())
                    print('-'*42)
                except Exception as e:
                    print(e)
                    print('This password was encrypted using different master password. Try joining the session with correct master password.')

            if value == 3:
                with conn:
                    curr.execute("DELETE FROM pwdb_table WHERE id = :id", {'id': num})  
                print('Successfully deleted ' + 'ID ' +str(num)+ ' from the database')
                print('')

def checkmasterpwd(secret_key, master_pwd):
    curr.execute("SELECT id, choosen,key FROM pwdb_table")
    passwithid = curr.fetchall()
    if len(passwithid)>0:
        passwithid= passwithid[-1]
        passenc= passwithid[2]
        reqdpass=passwithid[1].split(',')
        a,b,c,d= int(reqdpass[0]), int(reqdpass[1]),int(reqdpass[2]),int(reqdpass[3])
        cryp_key=secret_key[a:a+8]+master_pwd+secret_key[b:b+8]+master_pwd+secret_key[c:c+8]+master_pwd+secret_key[d:d+8]+ master_pwd
        cryp_key= cryp_key[0:32]
        cryp_key= base64.urlsafe_b64encode((cryp_key).encode())
        suite=Fernet(cryp_key)
        try:
            repass= suite.decrypt(passenc)
            print('Session joined successfully...')
        except:
            print('')
            print('WARNING! This master password you entered can not decrypt the last password previously saved here!')
            print('Using different master passwords is fine but it may cause conflicts! ')
            print('')
            print('Do you want to continue with this different master password? y/n ')
            print('Enter y if you want to continue with this master password, enter n to enter previously used master password.')
            print('')
            usr=input().lower()
            if usr!='y':
                print('Enter correct master password in the next session...')
                sys.exit()
            else:
                print('Session continued with different master password than previously entered...')

def showdatabase():
    '''prints all values stored inside sqlite database present in pwdb.db'''
    curr.execute("SELECT id, choosen,company,date,key FROM pwdb_table")
    passwithid = curr.fetchall()
    print('DATABASE: ')
    print(' ')
    for ids in passwithid:
        print(str(ids[0])+', '+ str(ids[2]) +', '+ str(ids[3]) +', ' +str(ids[1]) +', '+ str(ids[4]))
        print('_'*85)

project_folder = 'PasswordManager'
if not project_folder in os.listdir():
    os.makedirs(project_folder, exist_ok=True)

os.chdir(project_folder)
redir= os.getcwd()

if 'pwdb.db' not in os.listdir():
    conn = sqlite3.connect('pwdb.db')
    curr= conn.cursor()
    curr.execute("CREATE TABLE IF NOT EXISTS pwdb_table (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, choosen TEXT, company TEXT, date TEXT, key TEXT)")
    conn.commit()
    conn.close()

conn = sqlite3.connect('pwdb.db')
curr= conn.cursor()

def loop(secret_key, master_pwd):
    '''Loops continously generating a session of the entered master password, exits if value of 5 or greater than 5 provided.'''
    print('')
    print('_'*20)
    print('SESSION CONTINUED:')
    print('_'*85)
    print('1- store password')
    print('2- retrieve password')
    print('3- delete password')
    print('4- show database')
    print('5- exit')
    usr=input('-----------------> ')
    try:
        usr= int(usr)
        if usr==1:
            storepassword(secret_key, master_pwd)
            loop(secret_key, master_pwd)
        elif ((usr==2) or (usr==3)):
            retordel(usr,secret_key, master_pwd)
            loop(secret_key, master_pwd)
        elif usr==4:
            showdatabase()
            loop(secret_key, master_pwd)
        else:
            with conn:
                conn.execute('VACUUM')
            conn.close()
    except Exception as e:
        print(e)
        print('Enter numeric values...')
        loop(secret_key, master_pwd)

if __name__ == "__main__":
    print('Welcome to Python Password Manager!')
    print('_'*85)
    if len(sys.argv)>1:
        master_pwd= sys.argv[1]
    else:
        master_pwd=input("Enter master passord: ")
    secret_key=getsecretkey(master_pwd)
    checkmasterpwd(secret_key, master_pwd)
    loop(secret_key, master_pwd)
