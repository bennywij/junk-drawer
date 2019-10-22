#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 13:12:55 2019

@author: benny

- takes a pd dataframe
- takes a list of column names
- encrypts the columns
- returns the df
- uses block encryption so we consistently map the same string to the same ciphertext
- has option for hashing

Example Usage:
```
import secret_pandas as sec
df_encrypted = sec.encrypt_df_columns(df_original, ['col1', 'col2'], None)
df_decrypted = sec.decrypt_df_columns(df_encrypted, ['col1', 'col2'], 'secret_hex_file.secret')
```


"""


import os
from datetime import datetime
from Crypto.Cipher import AES

MULTIPLE_OF_SIXTEEN = 16 
# shouldn't need to change this -- it can be 16, 24, or 32 https://www.dlitz.net/software/pycrypto/api/current/Crypto.Cipher.AES-module.html
# currently no IV or salt is used

def generate_secret():
    """
    python 3 is nice with from binary .hex() and from hex to bytes .fromhex()
    """
    secret = os.urandom(MULTIPLE_OF_SIXTEEN).hex()

    with open("secret_hex_"+datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.secret', "w") as file:
        # We don't need write in binary mode anymore
        file.write(secret)

    return secret

def get_secret(secret_file_name_str):
    """
    We expect a hex encoded secret 
    """
    with open(secret_file_name_str,"r") as file:
        # we don't need to read in binary mode here
        secret = file.read()
    return secret    
    

def get_closest_larger_multiple_of_sixteen(n):
    remainder = n % 16
    if remainder == 0:
        return n
    else:
        return n+(16-remainder)


def encrypt_df_columns(df, list_of_columns, secret_file_name_str=None):

    if secret_file_name_str == None:
        secret = generate_secret()
    else:
        secret = get_secret(secret_file_name_str)

    # make the encryption object
    obj = AES.new(bytes.fromhex(secret))
    
    for col in list_of_columns:
        df[col]= df[col].apply(lambda x: obj.encrypt(str(x).ljust(get_closest_larger_multiple_of_sixteen(len(x)))).hex())
        # above tries to do "smart padding" by expanding to a multiple of 16 only if needed

    return df

def decrypt_df_columns(df, list_of_columns, secret_file_name_str):

    if secret_file_name_str == None:
        raise ValueError('Aborting -- we need a secret file to continue decrypt')
    else:
        secret = get_secret(secret_file_name_str)

    # make the encryption object
    obj = AES.new(bytes.fromhex(secret))
    
    for col in list_of_columns:
        df[col]= df[col].apply(lambda x: obj.decrypt(bytes.fromhex(x)).decode().strip())

    return df
        
def hash_df_columns(df, list_of_columns):

    for col in list_of_columns:
        df[col]= df[col].apply(lambda x: hash(str(x)))

    return df
