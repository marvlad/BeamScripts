# Script to check the BNB Beam with Crontab
# Author: Marvin Ascencio, ISU/FNAL Dec 31, 2022

import time
import urllib.request
from bs4 import *
import os
from datetime import datetime
import csv
import sys

filename = "/home/annie/beam_monitoring/bnb_values_out.cvs"

def get_time():
        obj = time.gmtime(0)
        epoch = time.asctime(obj)
        curr_time = round(time.time()*1000)
        return curr_time

def save_values(BNB_1, BNB_2, BNB_3, time, counter):
        delete_old_file = "rm "+filename
        os.system(delete_old_file)
        with open(filename, "a") as f:
                values_to_print = str(BNB_1)+", "+str(BNB_2)+", "+str(BNB_3)+", "+str(time)+", "+str(counter)
                print(values_to_print, file=f)

def get_BNB_web():
        my_request     = urllib.request.urlopen("https://www-bd.fnal.gov/notifyservlet/www")
        my_HTML        = my_request.read().decode("utf8")
        soup           = BeautifulSoup(my_HTML, "lxml")
        booster_beam   = soup.find("td", text="Booster Beam").find_next_sibling("td").string
        BNB_rate       = soup.find("td", text="BNB Rate").find_next_sibling("td").string
        BNB_1d_rate    = soup.find("td", text="BNB 1D Rate").find_next_sibling("td").string
        booster_beam_f = float(booster_beam)
        BNB_rate_f     = float(BNB_rate)
        BNB_1d_rate_f  = float(BNB_1d_rate)
        BNB_values = [booster_beam_f,BNB_rate_f,BNB_1d_rate_f,get_time()]
        return BNB_values

def read_values():
        read_values = []
        with open(filename, mode ='r')as file:
                csvFile = csv.reader(file)
                for lines in csvFile:
                        read_values = lines

        for i in range(0,len(read_values)):
                if(i<3):
                        read_values[i] = float(read_values[i])
                else:
                        read_values[i] = int(read_values[i])
        return read_values

def beam_status(val):
        if val[0] > 0.019 and val[1] > 0.001 and val[2] > 0.001:
                return True
        else:
                return False

def message_to(a,val,downtime):
        msg = ""
        if a == 1:
                msg = "The beam was down for ~"+str(downtime)+" minutes :scream:.\n Current values: \n   Booster Beam Intensity (E:TOR875) = "+str(val[0])+" E12 \n   BNB Rate = "+str(val[1])+" p/hr \n   BNB 1D Rate = "+str(val[2])+" Hz \n Check the status of the beam on the following pages: \n     * https://dbweb9.fnal.gov:8443/ifbeam/bmon/bnbmon/Display \n     * https://www-bd.fnal.gov/synoptic/display/BNB/BNBStatus  \n FIGURE IT OUT THE REASON on main Elog page: https://www-bd.fnal.gov/Elog/ \n You will be notified when the beam returns"
        if a == 2:
                msg = "The beam is BACK after ~"+str(downtime)+" minutes :partying_face:.\n Current values: \n   Booster Beam Intensity (E:TOR875) = "+str(val[0])+" E12\n   BNB Rate = "+str(val[1])+" p/hr \n   BNB 1D Rate = "+str(val[2])+" Hz \n See: https://dbweb9.fnal.gov:8443/ifbeam/bmon/bnbmon/Display"
        return msg

def send_slack(a,val,downtime):
        title="BNB ALERT "+str(val[0])
        message = message_to(a,val,downtime)
        if a == 1:
                #code="curl -X POST --data-urlencode \"payload={\\\"channel\\\": \\\"#shift\\\", \\\"username\\\": \\\""+title+"\\\", \\\"text\\\": \\\""+message+".\\\", \\\"icon_emoji\\\": \\\":rotating_light:\\\"}\" https:\/\/hooks.slack.com\/services\/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"
                code="curl -X POST --data-urlencode \"payload={\\\"channel\\\": \\\"#warnings\\\", \\\"username\\\": \\\""+title+"\\\", \\\"text\\\": \\\""+message+".\\\", \\\"icon_emoji\\\": \\\":rotating_light:\\\"}\" https:\/\/hooks.slack.com\/services\/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"
        if a == 2:
                #code="curl -X POST --data-urlencode \"payload={\\\"channel\\\": \\\"#shift\\\", \\\"username\\\": \\\""+title+"\\\", \\\"text\\\": \\\""+message+".\\\", \\\"icon_emoji\\\": \\\":zap:\\\"}\" https:\/\/hooks.slack.com\/services\/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" 
                code="curl -X POST --data-urlencode \"payload={\\\"channel\\\": \\\"#warnings\\\", \\\"username\\\": \\\""+title+"\\\", \\\"text\\\": \\\""+message+".\\\", \\\"icon_emoji\\\": \\\":zap:\\\"}\" https:\/\/hooks.slack.com\/services\/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"

        os.system(code)

def main():
        ov = read_values()
        nv = get_BNB_web()

        bstatus = beam_status(nv)

        # Checking if the beam is down
        if ov[4] < 6:
                if bstatus == True:
                        # save current values and counter 0
                        save_values(nv[0],nv[1],nv[2],nv[3],0)
                        print("Beam is fine")
                else:
                        # save the down time and add counter
                        if ov[4] < 1:
                                save_values(nv[0],nv[1],nv[2],nv[3],1)
                        else:
                                save_values(nv[0],nv[1],nv[2],ov[3],ov[4]+1)
                        if ov[4] == 5:
                                # send_slack()
                                send_slack(1,nv, ov[4])
        # Checking if the beam has returned
        else:
                if bstatus == False:
                        # increment the counter and save the keep the time 
                        save_values(nv[0],nv[1],nv[2],ov[3],ov[4]+1)
                else:
                        # Set counter to 0
                        # Send good news via slack
                        save_values(nv[0],nv[1],nv[2],nv[3],0)
                        send_slack(2,nv,ov[4])

if __name__ == '__main__':
        sys.exit(main())
