#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################################
# Indeed job scraper v0.2 (front end, status changer)
# Jan 21 2020
################################################################################################

import mysql.connector
import cgi
import cgitb
from mysql.connector import errorcode

cgitb.enable()
arguments = cgi.FieldStorage()
#print("Content-Type: text/html")
#print("")

job_id = arguments['id'].value
job_status = arguments['status'].value

try:
    cnx = mysql.connector.connect(user='js', password='****',
                                  host='localhost', database='job_scraper')
except mysql.connector.Error as err:
    import sys
    sys.exit(err)

cursor = cnx.cursor()
cursor.execute('update jobs set status="' + job_status +'" where id=' + job_id + ';')
#print('update jobs set status="' + job_status +'" where id=' + str(job_id) + ';')
cnx.commit()
cursor.close()
cnx.close()
