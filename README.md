# Python-Password-Manager
This Python 3 script can work as a password manager. It takes a master password and the script generates 640 characters secret key by using sha512 hashing of various combinations of the master password. Using various parts of this secret key and combining with original master password finally 32 characters are obtained which are then converted into Fernet Key and this Fernet Key encrypts the password and stores it in the sqlite3 database.

# Requirements:
- All other libraries used by this script are available as a built-in library except for one which is - cryptography. This can be installed using pip as 'pip install cryptography' or it can also be installed by running the 'requirements.py' file available in this repository as python requirements.py

# Using the script:
- The script can be run as python pwdm.py and a master password is asked. This same master password will be used for encryption and decryption of the passwords for the whole session. When passwords are stored they can be decrypted only by using the same master password which was used for its encryption.
- The master password can also be provided as a command-line argument as python pwdm.py, my_master_password
