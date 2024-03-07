### Author Sriharsha Dhanekula (hdhaneku@cisco.com)
## This does 4 things: updates default password, imports credentials for devices, providers, tags, Onboards the devices using the CNC API Calls

'''
Step 1: Update Default Password
Step 2: Import Credentials/ Tags/ Provider/ Devices
Input: {Hardcoded}
CW IP
default username/password {User can do it for there own user too as first time login}
New Password
Input Files: {CSV Files}
Devices.csv , Credentials.csv, Provider.csv, Tags.csv
'''

import sys
import time
import json
import base64
import requests
from collections import OrderedDict

cw_ip = "10.10.10.10"
username = "admin"
pass_to_reset = "admin"

password = "Cwork123!"
device_csv = "Device.csv"
credentials_csv = "Credential.csv"
provider_csv = "Provider.csv"
tags_csv = "Tag.csv"

ACCEPTED_CODES = [200, 201, 204]
cw_url = "https://" + cw_ip + "/30603"


def token(user, passw):
    '''
    Follow Crosswork API 2 step process to generate JWT via TGT
    :param user: Crosswork Username
    :param passw: Password
    :return: JWT token for Crosswork API requests
    '''
    TOKEN_HEADERS = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
    TOKEN_URI = "/crosswork/sso/v1/tickets"

    tgt_url = cw_url + TOKEN_URI + "?username="+user+"&password="+passw
    TGT = requests.post(tgt_url, data="", headers=TOKEN_HEADERS, verify=False)

    jwt_url = cw_url + TOKEN_URI + "/" +  str(TGT.content.decode())
    jwt_payload = "service="+ cw_url + "/app-dashboard"
    JWT = requests.post(jwt_url, data=jwt_payload, headers=TOKEN_HEADERS, verify=False)

    return str(JWT.content.decode())

def update_default_password(user, defpass, newpass, expected_code=ACCEPTED_CODES):
    print("Update Default Password")
    try:
        jwt_token = token(user, defpass)
        url = cw_url + '/crosswork/password/v1'
        header = {'Content-Type': 'application/json; charset=UTF-8', 'Accept': 'application/json',
                  'Authorization': 'Bearer ' + jwt_token}
        payload = {
            "OldPassword": defpass,
            "NewPassword": newpass
        }
        response = requests.request("PUT", url, headers=header, data=payload)
        response_code = response.status_code()
        if response_code in expected_code:
            print("Default Password reset succesfully")

    except:
        print("Error in default password change as: " + response_code + " " + response)
        raise

def file2base64(filename):
    try:
        with open(filename, "rb") as csvFile:
            read_string = csvFile.read()
            file_string = base64.b64encode(read_string).decode()
            return file_string
    except Exception as err:
        print("Unable to get data from the CSV file with error: " + str(err))
        raise

def csv_upload(csv_name, ftype, expected_code=ACCEPTED_CODES):
    try:
        url = cw_url + "/crosswork/inventory/v1/csvupload"
        HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json'}

        csv = file2base64(csv_name)

        payload_dict = OrderedDict()
        payload_dict['type'] = ftype
        payload_dict['csv'] = csv
        payload_dict['is_dryrun'] = "false"
        payload = json.dumps(payload_dict)

        response = requests.request("POST", url, headers=HEADERS, data=payload)
        response_code = response.status_code()
        if response_code in expected_code:
            print("Default Password reset succesfully")

        return response_code

    except Exception as err:
        print("Unable to upload CSV file with error: " + response_code + " " + str(err))
        raise


def main(argv):

    print("Welcome!! \n \n Script will be performing some day0 tasks for user as")
    print("Task1: Update Default Password")
    #Comment below section to avoid password reset
    update_default_password(username, pass_to_reset, password)
    time.sleep(3) #wait for 3 second for no reason

    print("Task2: Import Credentials/ Tags/ Provider/ Devices")
    # Comment below section to avoid CSV import

    #Import Credential
    res1 = csv_upload(credentials_csv, ftype=3)
    print("Credentials uploaded response: " + str(res1))

    #Import Tag
    res2 = csv_upload(tags_csv, ftype=4)
    print("Tags uploaded response: " + str(res1))

    #Import Provider
    res3 = csv_upload(provider_csv, ftype=2)
    print("Provider uploaded response: " + str(res1))

    #Import Devices
    res4 = csv_upload(device_csv, ftype=1)
    print("Devices uploaded response: " + str(res1))


if __name__ == "__main__":
    main(sys.argv[1:]) 