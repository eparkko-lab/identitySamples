import sys
import base64
import requests
import re

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

configs = {    
    'tokenEndpoint':'https://login.microsoftonline.com/',
    'graphEndpoint':'https://graph.microsoft.com/v1.0/',
    'clientId':'c759a33f-04be-4355-bc18-f6743a3268ed',
    'clientSecret':'see password vault', 
    'scopes':'https://graph.microsoft.com/.default',
    'tenantId':''
}

def setHTTPHeaders():
    
    return {                       
        'Content-Type': 'application/x-www-form-urlencoded'
        }

def getGraphAccessToken():  
    print('Trying HTTP POST to get access token')
    requestHeaders = setHTTPHeaders()
    requestBody={'grant_type':'client_credentials',
                'client_id':configs['clientId'],
                'client_secret':configs['clientSecret'],
                'scope':configs['scopes']}
    tokenEndpoint = configs['tokenEndpoint']+configs['tenantId']+'/oauth2/v2.0/token'      
    response = requests.post(tokenEndpoint,data=requestBody,headers=requestHeaders, verify=False)
    if (response.status_code == 200):
        accessToken=response.json()['access_token']    
        return accessToken
    else:
        print(response.status_code)
        print(response.content)
        return None

def getGroup(accessToken, groupName):
    print('\nTrying HTTP GET for /groups')
    
    params={'$filter':'startswith(displayName, \''+groupName+'\')'}
    headers={'Authorization':'Bearer '+ accessToken,
            'Content-Type':'application/json'}
    groupsEndpoint = configs['graphEndpoint']+'groups'   
    response = requests.get(groupsEndpoint,headers=headers,params=params, verify=False)
    if (response.status_code == 200):
        groups=response.json()['value']
        if len(groups)>0:
            groupId=response.json()['value'][0]['id']
            print("Group retrieved id:")
            return True, groupId
        else:
            return False, None    
    else:
        print(response.status_code)
        print(response.content)
        return False, None   

def deleteGroup(accessToken, groupId):
    print('\nTrying HTTP DELETE for /groups/'+groupId)
    
    headers={'Authorization':'Bearer '+ accessToken,
            'Content-Type':'application/json'}
    groupsEndpoint = configs['graphEndpoint']+'groups/'+groupId   
    response = requests.delete(groupsEndpoint,headers=headers, verify=False)
    if (response.status_code == 204):
        print("Group deleted")
        return True
    else:
        print(response.status_code)
        print(response.content)
        return False

def createGroup(accessToken):
    print("Trying HTTP POST for /groups")
    requestBody={
        "description": "Created by python test script",
        "displayName": "PythonTest",
        "groupTypes": [],
        "mailEnabled": False,
        "mailNickname": "na",
        "securityEnabled": True
        }
    headers={'Authorization':'Bearer '+ accessToken,
            'Content-Type':'application/json'}
    groupsEndpoint = configs['graphEndpoint']+'groups'   
    response = requests.post(groupsEndpoint,json=requestBody,headers=headers, verify=False)
    if (response.status_code == 201):
        groupId=response.json()['id']    
        return True, groupId
    else:
        print(response.status_code)
        print(response.content)
        return False, None   

def main():
    accessToken=getGraphAccessToken()
    print('\nAccess Token:')
    print(accessToken)
    
    groupExists,groupId=getGroup(accessToken,'PythonTest')
    if groupExists and len(groupId)>=1:
        print('group PythonTest already exists')
        print('Now deleting group PythonTest')
        deleteGroup(accessToken,groupId)
        print('creating group PythonTest')
        created,groupId=createGroup(accessToken)
        print('Now deleting group PythonTest')
        deleteGroup(accessToken,groupId)
    else:
        print('group PythonTest does not exist')
        print('creating group PythonTest')
        created,groupId=createGroup(accessToken)
        print('Now deleting group PythonTest')
        deleteGroup(accessToken,groupId) 
main()