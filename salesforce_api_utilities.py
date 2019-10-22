# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 13:34:33 2018
@author: benny

Generic SalesForce tools

Requires simple_salesforce
https://github.com/simple-salesforce/simple-salesforce

"""

from simple_salesforce import Salesforce
import datetime

# constants -- managed this in salesforce webUI -- Manage Users. New tokens come with new passwords.
USERNAME = username
PASSWORD = password
TOKEN = token


def connect():
    sf_connection = Salesforce(username=USERNAME, password=PASSWORD, security_token=TOKEN)
    return sf_connection


# create n intervals of 100 each up to length of records
# write code that will do this x at a time and cycle through 100 at a ttime
# necessary to avoid timeouts with SalesForce's API

def batchUploadToSalesForce(data=None, batch_size=50, type=None, sf_connection=None, debugmode=False): 
       
    BATCH_SIZE = batch_size

    def uploadToSF(type,data):    
        if type == 'Lead': 
            results = sf_connection.bulk.Lead.update(data) 
        elif type == 'Opportunity':
            results = sf_connection.bulk.Opportunity.update(data) 
        elif type == 'Contact':
            results = sf_connection.bulk.Contact.update(data)
        elif type == 'Account':
            results = sf_connection.bulk.Account.update(data)
        elif type == 'ACTDDEV__EAST_FinancialAccount__c': # custom data type
            results = sf_connection.bulk.ACTDDEV__EAST_FinancialAccount__c.update(data)
        else:
            print ('unrecognized SF type')
        #print '3s artificial delay'
        #time.sleep(3)
        return results
    
    if len(data) <= BATCH_SIZE:
        results = uploadToSF(type, data)
    else:
         
        thresholds = [] 
        n = int(len(data)/BATCH_SIZE)    
        for i in range(1,n+1):    
            thresholds.append(i*BATCH_SIZE-1)       
        # are there any left?
        if thresholds[len(thresholds)-1] != len(data)-1:            
            thresholds.append(len(data)-1)
        # zero start and with indexing the right edge is never included!
        
        # first batch
        assert len(data[0:thresholds[0]+1]) == BATCH_SIZE

        #print len(data[0:thresholds[0]+1])
        results = uploadToSF(type,data[0:thresholds[0]+1])
        
        # subsequent batches
        
        if len(data) % BATCH_SIZE == 0:
        # if there is no remainder set, we cut the range by 1 to avoid indexing out of threshold
            n = n-1
        
        for i in range(0,n):
            if debugmode == True:
                print(type)
                print(datetime.datetime.today()) 
                print(str(len(data))+' total records')
                print(str(i+1)+' of '+str(n)+' subsequent batches')
            #print i
            #print n
            #print len(data[thresholds[i]+1:thresholds[i+1]+1])

            #assert len(data_leads[thresholds[i]+1:thresholds[i+1]+1]) == BATCH_SIZE
            results.extend(uploadToSF(type,data[thresholds[i]+1:thresholds[i+1]+1])) # out of range error when batch size is perfect multiple and remainder is zero
            
    return results


def getContactSpoofId(sf_connection=None):
    
    results = sf_connection.query_all("SELECT Id, Spoof_ID__c FROM Contact")
    
    return results
