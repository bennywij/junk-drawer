#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 08:18:19 2019

@author: benny


Utility functions that help us put CSVs or DFs into a vertica db
Takes advantage of Vertica 8 Flex Tables so we don't have to specify columns or column names upfront

upload_df_to_existing_table will assume existence of a target table and will COPY new rows into it

Use this when you need it as part of a chain or automation.

For one-offs, use COPY ... FROM LOCAL
See: https://www.vertica.com/docs/9.2.x/HTML/Content/Authoring/FlexTables/LoadCSVData.htm

Example use:

Assumes we have an importable library called vertica_custom.py with connection strings for example:

```
import vertica_python

conn_info = {'host': hostname, 
             'port': portnum,
             'user': username,
             'password': password,
             'database': 'dbname',
             # 5 minutes timeout on queries
             'read_timeout': 300} # in seconds


def connect():
    connection = vertica_python.connect(**conn_info)
    return connection
```

Then:
```
import vertica_custom
import upload_to_vertica

rows_uploaded = upload_to_vertica.upload_df(vertica_obj=vertica
                                  , target_flex_table_name='CSB_CustAcct_20190724'
                                  , pandas_df=df_latest_cust_acct_encr)


# if from CSV
rows_uploaded = upload_to_vertica.upload_csv(vertica_obj=vertica
                                  , target_flex_table_name='CSB_CustAcct_20190724'
                                  , path_to_local_csv='/Users/benny/Downloads/CSB CustAcct/CSB_CustAcct_20190724.csv')
```

"""



create_SQL="""
CREATE FLEX TABLE {table_name}();
"""

copy_SQL="""COPY {table_name} FROM STDIN PARSER fcsvparser() REJECTED DATA AS TABLE reject_rows_{table_name};""" 

flex_view_SQL="""
SELECT compute_flextable_keys_and_build_view('{table_name}');
"""

rowcount_SQL="""
SELECT count(1) FROM {table_name}_view;
"""




def upload_csv(vertica_obj, target_flex_table_name, path_to_local_csv):
    """
    Expects to exist already a CSV in local file system with a header
    Need well formed CSV utf-8 encoded
    Returns row count of uploaded target -- compare that to what you upload
    """

    TABLE_NAME = target_flex_table_name
    LOCAL_PATH = path_to_local_csv  # must be on your machine
    
    conn = vertica_obj.connect()    
    cursor = conn.cursor()

    cursor.execute(create_SQL.format(table_name=TABLE_NAME))  
    
    with open(LOCAL_PATH, "rb") as file:
        for_stdin = file.read().decode('utf-8','ignore')
        cursor.copy(copy_SQL.format(table_name=TABLE_NAME), for_stdin) 
        conn.commit()
    
    cursor.execute(flex_view_SQL.format(table_name=TABLE_NAME))

    cursor.execute(rowcount_SQL.format(table_name=TABLE_NAME))
    rows = cursor.fetchall()[0][0]
    
    conn.close()
    
    return rows    



def upload_df(vertica_obj, target_flex_table_name, pandas_df):
    """
    Expects to exist a pandas dataframe
    Returns row count of uploaded target -- compare that to what you upload
    """

    TABLE_NAME = target_flex_table_name
    
    conn = vertica_obj.connect()    
    cursor = conn.cursor()

    cursor.execute(create_SQL.format(table_name=TABLE_NAME))  
    
    for_stdin = pandas_df.to_csv(sep=',',index=False)
    cursor.copy(copy_SQL.format(table_name=TABLE_NAME), for_stdin) 
    conn.commit()
    
    cursor.execute(flex_view_SQL.format(table_name=TABLE_NAME))

    cursor.execute(rowcount_SQL.format(table_name=TABLE_NAME))
    rows = cursor.fetchall()[0][0]
    
    conn.close()
    
    return rows    


def upload_df_to_existing_table(vertica_obj, target_table_name, pandas_df):
    """
    Expects to exist a pandas dataframe
    Returns TOTAL row count of uploaded target -- compare that to what you upload vs known previous
    """

    TABLE_NAME = target_table_name
    
    conn = vertica_obj.connect()    
    cursor = conn.cursor()
    
    for_stdin = pandas_df.to_csv(sep=',',index=False, header=False)
    cursor.copy(copy_SQL.format(table_name=TABLE_NAME), for_stdin) 
    conn.commit()
    
    cursor.execute(rowcount_SQL.format(table_name=TABLE_NAME))
    rows = cursor.fetchall()[0][0]
    
    conn.close()
    
    return rows    

