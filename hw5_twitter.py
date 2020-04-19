#########################################
##### Name: Bhawna Agarwal          #####
##### Uniqname: bhawna              #####
#########################################

from requests_oauthlib import OAuth1
import json
import requests
import secrets # file that contains your OAuth credentials
import xml.etree.ElementTree as ET

client_key = secrets.GOODREADS_API_KEY
client_secret = secrets.GOODREADS_API_SECRET
params = {'v':'2', 'id': '20227451', 'search[query]':'Sapiens'}

''' Helper function that returns an HTTP 200 OK response code and a 
representation of the requesting user if authentication was 
successful; returns a 401 status code and an error message if 
not. Only use this method to test if supplied user credentials are 
valid. Not used to achieve the goal of this assignment.'''

#url = "https://www.goodreads.com/review/list?v=2"
#auth = OAuth1(client_key, client_secret)
#response = requests.get(url, auth=auth, params=params)
tree = ET.parse('out.xml')
print(tree)
#print (response.text)



    
