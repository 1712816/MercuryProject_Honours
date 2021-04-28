import json
import boto3
from botocore.exceptions import ClientError

import imaplib
import email
from email.header import decode_header
from email.parser import HeaderParser
import webbrowser
import os

import time

# -----------------------------------------------------------Email Retrieving Global Variables----------------------------------------------------------------

# account credentials
username = "admin@cmbsoftwareengineer.awsapps.com"
password = "Password"



# -----------------------------------------------------------Pinpoint Global Variables----------------------------------------------------------------
# The AWS Region that is being used to send the message. Ireland
region = "eu-west-1"

# The title that appears at the top of the push notification.
title = ""

message = ""

# The Amazon Pinpoint project/application ID to use when you send this message.
application_id = "9069ad0a6c69457caf10b80c8b6b2f76"


# The action that should occur when the recipient taps the message. Possible
# values are OPEN_APP (opens the app or brings it to the foreground),
#   DEEP_LINK (opens the app to a specific page or interface), or URL (opens a
# specific URL in the device's web browser.)
action = "OPEN_APP"

# This value is only required if you use the URL action. This variable contains
# the URL that opens in the recipient's web browserself.
url = "https://www.example.com"

# The priority of the push notification. If the value is 'normal', then the
# delivery of the message is optimized for battery usage on the recipient's
# device, and could be delayed. If the value is 'high', then the notification is
# sent immediately, and might wake a sleeping device.
priority = "high"

# The amount of time, in seconds, that the push notification service provider
#   (such as FCM or APNS) should attempt to deliver the message before dropping
# it. Not all providers allow you specify a TTL value.
ttl = 600


# ---------------------------------------------------------------------------------------------------------------------------

# Set the MessageType based on the values in the recipient variable.
def create_message_request(title, message):

    token = "cm1OosM3KuE:APA91bGJPgdWc2gh-Iu20sVIFL1klSPV6wUm-OASuUqPoJqQecMHfm3d5kY1a0p3WGAIz3HTbvBti0rkCKl5pvN5xf54BW8vntH16Qjj4jcv_L14DkxmGlQlPRYdQrQlzkdsr6ngDkjX"
    service = "GCM"

    if service == "GCM":
        message_request = {
            'Addresses': {
                token: {
                    'ChannelType': 'GCM'
                }
            },
            'MessageConfiguration': {
                'GCMMessage': {
                    'Action': action,
                    'Body': message,
                    'Priority' : priority,
                    'SilentPush': False,
                    'Title': title,
                    'TimeToLive': ttl,
                    'Url': url,
                    "ImageIconUrl": "https://i.imgur.com/2aw4n2W.png",
                    "SmallImageIconUrl":"https://i.imgur.com/2aw4n2W.png"
                }
            }
        }
   
    else:
        message_request = None

    return message_request

# Show a success or failure message, and provide the response from the API.
def show_output(response):
    if response['MessageResponse']['Result']['cm1OosM3KuE:APA91bGJPgdWc2gh-Iu20sVIFL1klSPV6wUm-OASuUqPoJqQecMHfm3d5kY1a0p3WGAIz3HTbvBti0rkCKl5pvN5xf54BW8vntH16Qjj4jcv_L14DkxmGlQlPRYdQrQlzkdsr6ngDkjX']['DeliveryStatus'] == "SUCCESSFUL":
        status = "Message sent! Response information:\n"
    else:
        status = "The message wasn't sent. Response information:\n"
    print(status, json.dumps(response,indent=4))

# Send the message through the appropriate channel.
def send_message(title, message):

    token = "cm1OosM3KuE:APA91bGJPgdWc2gh-Iu20sVIFL1klSPV6wUm-OASuUqPoJqQecMHfm3d5kY1a0p3WGAIz3HTbvBti0rkCKl5pvN5xf54BW8vntH16Qjj4jcv_L14DkxmGlQlPRYdQrQlzkdsr6ngDkjX"
    service = "GCM"
    
    message_request = create_message_request(title, message)

    client = boto3.client('pinpoint',region_name=region)

    try:
        response = client.send_messages(
            ApplicationId=application_id,
            MessageRequest=message_request
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        show_output(response)
        


def retrieving_email():
   
   #connecting to the email server
    M = imaplib.IMAP4_SSL('imap.mail.eu-west-1.awsapps.com')
   
   #Login into the email and seleting the inbox folder
    M.login(username, password)
    M.select('inbox')
    data = M.search(None, 'ALL')
    mail_ids = data[1]
    id_list = mail_ids[0].split()
    #receiving the latest email
    latest_email_id = int(id_list[-1])
    
    data = M.fetch(str(latest_email_id), '(RFC822)')
    
    #retrieving the email and subject
    for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    msg = email.message_from_string(str(arr[1],'utf-8'))
                    email_subject = msg['subject']
                    email_from = msg['from']
                    
                    email_body = ""
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))

                            # skip any text/plain (txt) attachments
                            if ctype == 'text/plain' and 'attachment' not in cdispo:
                                email_body = part.get_payload()  # decode
                                break
                    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
                    else:
                        email_body = msg.get_payload()
                    
    #closing the connectiion and loggingout the email
    M.close()
    
    return email_body, email_subject
    
    
def writing_message(email_body, email_subject):
    
    title = ""
    message = ""
    
    #converting entire email to upperase for ease of string modifications
    email_body = email_body.upper()
    email_subject = email_subject.upper()
    
    print(email_body)
        
    #filtering the email for the notifications
    if 'YELLOW WARNING' in email_subject:
            
        title = "YELLOW WARNING FOR "
        message = "The MetOffice has issued a YELLOW warning for "
        
        print("generating yellow warning")
            
            
    if "AMBER WARNING" in email_subject:
            
        title = "AMBER WARNING FOR "
        message = "Be careful the MetOffice has issued a AMBER warning for "
            
    if "RED WARNING" in email_subject:
        title = "RED WARNING FOR "
        message = "Be very careful the MetOffice has issued a RED warning for "
            
    if "RAIN" in email_subject:
        message = message + "Rain "
        title = title + "HEAVY RAIN "
            
    if "ICE" in email_subject:
        message = message + "Ice  "
        title = title + "ICE "
            
    if "FOG" in email_subject:
        message = message + "FOG "
        title = title + "HEAVY FOG "
                
    if "WIND" in email_subject:
        message = message + "WIND "
        title = title + "STRONG WIND "
                
    if "SNOW" in email_subject:
        message = message + "Snow "
        title = title + "HEAVY SNOW "
                
    message = message + "in the area, what to expect - "
        
    #Getting the headline and plaing it into the notification
    headline = email_body.split("HEADLINE",1)[1]
        
    message = message + headline.split(".",1)[0].lower()
        
    return title, message        
        
        
def lambda_handler(event, context):

    time.sleep(15)
    
    email_body, email_subject = retrieving_email()
    
    title, message = writing_message(email_body, email_subject)
    
    print(message)
    
    send_message(title, message)
    
    print("SUCCESSFUL")
