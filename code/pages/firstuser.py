import streamlit as st
import sqlite3
import pyaes
import os
import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

salt = b'\xb4\xa7\xf3\x92\xc4,\xf6\xacY\x18eb\x80\xf4\xae\xea!fJ\xc3\xbd\xae*,\xdeZF\xe5g\xa5\xd9\x8d(\x15\x90\xfd!\xdaU\'\x8aK\xfe\x8e\xfa%\xfc\xd2\x0e1\x1d\xe8H\xbc"\xb0\xf7D\x120\n8q\xc8g\x7f\x1d\t\x10o\xb9v;u\xd1v\x9e#k\x9e3<\xfc\xdf\x85H\xd5\x11)b"\x10\xf9*\x80\xc8\xe7\x0e\x1f@\x03q\x0c\xd2\x01<\xc0\xd3C\xd4\x0b\x14\xf3\xa6\r\xb9qs\x92G\xd0\xad\xb5\x96=\xce\xe1\xab\xe2\xa1}rw\x8b\xa9uG\x15\xb2)\x95^"\xb7\xee1M\xd6\x00\xa8^J\xedV\xb3m\x18`&\xc5\x7f)\x13#}8F\xb4\xf0\x02y\xfaK\xeb\xab\x02\xeb\xe9Li\x85\xe7b\xa1\xd5\xef\xf7\xfeR\x92\x97T\xf3j\xfd\x87x\xe1\x82\xb0\x88\xbc\xf5[\x9e\xe9\xea\xdd\xe0\x0b\x9b\xfd\rb\xc8;\x95t\xd3\x80"w\\\xd7\xe4%Y \xe5\xdb\xd8\xcd\x04u\xb0\xc2\xa2\x05\x0cM\x8a^\xabO~y\xd7\xf7\x89\x85\xd2\x04YB\xcb\x14'
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)

key = kdf.derive(b"Admin1!")

conn= sqlite3.connect('Project.db')
c=conn.cursor()

aes = pyaes.AESModeOfOperationCTR(key)

name = st.text_input("UserName")
password = st.text_input("Password",type='password')
website = st.text_input("Website")

button,button1=st.columns(2)
with button:
    button=st.button("Submit")
with button1:
    gen=st.button("Generate")



#Password Strength Function
def password_strength(s):
    c1=[[65,90],[97,122],[48,57]] #Set1-Upper case, Set2-Lower case, Set3-Numbers
    c2=[33,35,36,42,91,93,94,95,123,125] #Set of Special characters
    f=[0]*5 # checklist to check if the password is satisfying all the conditions or not
    for i in s:
        c=0
        flag=0
        for j in c1:
            #if it has Upper case set the f[0]=1
            #Lowercase f[1]=1
            #numbers f[2]=1
            #Special characters f[3]=1
            if j[0]<=ord(i) and j[1]>=ord(i) and f[c]!=1:
                f[c]=1
                flag=1
                break
            c+=1
        if ord(i) in c2 and flag==0:
            f[3]=1
    #if the password having length more than 8, f[4]=1
    if f[4]==0 and len(s)>=8:
        f[4]=1
    return f.count(1)/5  #scores would be [0.2, 0.4, 0.6, 0.8, 1]


def generate():
    c1=[[65,90],[97,122],[48,57]]
    c2=[33,35,36,42,91,93,94,95,123,125]
    f=[0]*5
    #raondom number for password length
    n=random.randint(8,12)
    Password=''
    c=1
    for i in range(n):
        if c==1:
            for j in c1:
                #generating the character using the ascii range from the c1
                Password+=chr(random.randint(j[0],j[1]))
        elif c==0:
            #generating the special character using the ascii range from the c1
            Password+=chr(c2[random.randint(0,len(c2)-1)])
        #randomising to choose either c1 or c2 for every character
        c=random.randint(0,1)
    return Password



if gen:
    generate=st.text_input("Generated Password",value=generate())

if button:
    # conditon for password strength
    score=password_strength(password)
    if score>=0.6 and score<=0.8:
        st.warning("Password is not upto criteria. Change it!!")
    if score<0.6:
        st.error("Bad Password!!")
    c.execute('Select * from users where username==(?);',(name,))
    n=list(c.fetchall())
    # if and only its completely fine then let it go furthure process
    if len(n)==0 and name!='' and score==1:
        try:
            #check if the username is taken or not. if not push it into DB
            password=aes.encrypt(password)
            c.execute('select max(ID) from users;')
            n=list(c.fetchone())
            if n==[None]:
                n[0]=0
            c.execute('INSERT INTO users(ID, website, username, password) VALUES(?,?,?,?)',(n[0]+1,website,name,password))
            c.execute('commit;')
            st.success("Congrats, You are successfully signed up")
        except:
            print("failed")
    elif len(n)==1 and name!='':
        # check if the creds are exactly matching with the DB
        if n[0][1]==name and n[0][2]==password:
            st.error("since u already have an account, use this creds to sign in")
        # prompt for the username taken
        else:
            st.error("Username is already Taken")