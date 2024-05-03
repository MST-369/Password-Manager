import streamlit as st
import sqlite3
import pandas as pd
import pyaes
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

##Key Derivation from Admin Password

salt = b'\xb4\xa7\xf3\x92\xc4,\xf6\xacY\x18eb\x80\xf4\xae\xea!fJ\xc3\xbd\xae*,\xdeZF\xe5g\xa5\xd9\x8d(\x15\x90\xfd!\xdaU\'\x8aK\xfe\x8e\xfa%\xfc\xd2\x0e1\x1d\xe8H\xbc"\xb0\xf7D\x120\n8q\xc8g\x7f\x1d\t\x10o\xb9v;u\xd1v\x9e#k\x9e3<\xfc\xdf\x85H\xd5\x11)b"\x10\xf9*\x80\xc8\xe7\x0e\x1f@\x03q\x0c\xd2\x01<\xc0\xd3C\xd4\x0b\x14\xf3\xa6\r\xb9qs\x92G\xd0\xad\xb5\x96=\xce\xe1\xab\xe2\xa1}rw\x8b\xa9uG\x15\xb2)\x95^"\xb7\xee1M\xd6\x00\xa8^J\xedV\xb3m\x18`&\xc5\x7f)\x13#}8F\xb4\xf0\x02y\xfaK\xeb\xab\x02\xeb\xe9Li\x85\xe7b\xa1\xd5\xef\xf7\xfeR\x92\x97T\xf3j\xfd\x87x\xe1\x82\xb0\x88\xbc\xf5[\x9e\xe9\xea\xdd\xe0\x0b\x9b\xfd\rb\xc8;\x95t\xd3\x80"w\\\xd7\xe4%Y \xe5\xdb\xd8\xcd\x04u\xb0\xc2\xa2\x05\x0cM\x8a^\xabO~y\xd7\xf7\x89\x85\xd2\x04YB\xcb\x14'
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)

key = kdf.derive(b"Admin1!")

## connect to the database and create a instance of cursor for command execution
conn = sqlite3.connect('Project.db')
c = conn.cursor()

# st.text_input for field inputs from the UI
name = st.text_input("Admin Username",value="ManiSurya369")
password = st.text_input("Password", type='password',value='Admin1!')

#dividing the Columns into 2 
Manage,Retrieve=st.columns(2)

# Defining the Manage Functionality
with Manage:
    ID = st.text_input("Enter the ID number to remove the user")
    m=st.button("Manage/Remove")
    if m:
        #Cross verifying if the entered Creds are existed in DB
        c.execute('SELECT * FROM admins;')
        admins = c.fetchall()
        creds = [(admin[1], admin[2]) for admin in admins]

        # if Yes remove the User from DB
        if (name, password) in creds:
            c.execute("Select * from users where ID=(?)",(ID))
            n=list(c.fetchall())
            if len(n):
                c.execute('Delete from users where ID=(?)',(ID,))
                c.execute('commit;')
                st.success("USER HAS BEEN REMOVED SUCCESSFULLY!!")
            else:
                st.warning("NOT FOUND IN DATABASE")
        # Else Display the Prompt
        else:
            st.error("INVALID CREDS")

#Define the Retrieve Function
with Retrieve:
    r=st.button("Retrieve")
    if r:
        # Looking for Entered Creds in DB
        c.execute('SELECT * FROM admins;')
        admins = c.fetchall()
        creds = [(admin[1], admin[2]) for admin in admins]
        #if Yes, then decrypt and display the creds to Master
        if (name, password) in creds:
            c.execute('SELECT * FROM users;')
            users = c.fetchall()
            display=[]
            if len(users):
                for i in range(len(users)):
                    aes = pyaes.AESModeOfOperationCTR(key)
                    display.append([users[i][0],users[i][1],users[i][2],aes.decrypt(users[i][3]).decode('utf-8')])
                st.write(pd.DataFrame(display,columns=['ID','Website','Username','Passwords`  ']))
            else:
                st.warning("NO USER IN DATABASE")
        #else display the prompt
        else:
            st.error("INVALID CREDS")