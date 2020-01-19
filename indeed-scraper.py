#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################################
# Indeed job scraper v0.1
# Jan 12 2020
################################################################################################
import requests
import re
import time
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from bs4 import BeautifulSoup

def write_log(data):
    log_file = open(r"/root/python/webscraper/ws.log","a")
    log_file.write(data + '\n')
    log_file.close()

def extract_jobs(job_list_blocks):
    try:
        cnx = mysql.connector.connect(user='js', password='****',
                                  host='localhost', database='job_scraper')
    except mysql.connector.Error as err:
        import sys
        sys.exit(err)
    for job_list_block in job_list_blocks:
        #
        # Grabbing job title and link
        job_title = job_list_block.find('a', class_='jobtitle turnstileLink')
        if job_title != None:
            job_title_s = str(job_title['title'])
            job_link_s = str(job_title['href'])
        else:
            job_title_s = ''
            job_link_s = ''
            write_log('\n(!) job_title not found')
            write_log(str(job_list_block))
        job_title_s = job_title_s.strip()
        job_link_s = job_link_s.strip()
        #
        # Grabbing company name
        job_company = job_list_block.find('span', class_='company')
        if job_company != None:
            job_company_s = str(job_company.text)
        else:
            job_company_s = 'Unknown'
            write_log('\n(!) job_company not found')
            write_log(str(job_list_block))
        job_company_s = job_company_s.strip()
        #
        # Grabbing main location
        job_location_main = job_list_block.find('div', class_='recJobLoc')
        if job_location_main != None:
            job_location_main_s = str(job_location_main['data-rc-loc'])
        else:
            job_location_main_s = ''
            write_log('\n(!) job_location_main not found')
            write_log(str(job_list_block))
        job_location_main_s = job_location_main_s.strip()
        #
        # Grabbing extra location
        job_location = job_list_block.find('span', class_='location accessible-contrast-color-location')
        if job_location == None:
            job_location = job_list_block.find('div', class_='location accessible-contrast-color-location')
        if job_location != None:
            job_location_s = str(job_location.text)
        else:
            job_location_s = ''
            write_log('\n(!) job_location not found')
            write_log(str(job_list_block))
        job_location_s = job_location_s.strip()
        #
        # Grabbing job marks
        job_easily_apply_s = 'N'
        job_urgently_hiring_s = 'N'
        job_marks = job_list_block.findAll('td', class_='jobCardShelfItem')
        for job_mark in job_marks:
            job_mark_s = str(job_mark.text)
            if job_mark_s.strip() == 'Easily apply':
                job_easily_apply_s = 'Y'
            if job_mark_s.strip() == 'Urgently hiring':
                job_urgently_hiring_s = 'Y'
        print('EA: ' + job_easily_apply_s)
        print('UH: ' + job_urgently_hiring_s)
        #
        # Grabbing job summary
        job_summary = job_list_block.find('div', class_='summary')
        if job_summary != None:
            job_summary_s = str(job_summary)
            job_summary_s = re.sub(' style=".*"', '', job_summary_s)
        else:
            job_summary_s = ''
            write_log('\n(!) job_summary not found')
            write_log(str(job_list_block))
        job_summary_s = job_summary_s.strip()
        #
        # Parsing job page
        # Grabbing job description
        time.sleep(0.2)
        page = requests.get('https://indeed.com' + job_link_s)
        soup = BeautifulSoup(page.content, 'html.parser')
        job_full = soup.find('div', class_='jobsearch-JobComponent icl-u-xs-mt--sm')
        job_description = job_full.find('div', class_='jobsearch-jobDescriptionText')
        if job_description != None:
            job_description_s = str(job_description)
            write_log(job_description_s + '\n')
        else:
            job_description_s = ''
            write_log('\n(!) job_description not found')
            write_log(str(job_full))
        #
        # Grabbing wage and offer
        job_wage_s = ''
        job_offer_s = ''
        job_metadata = job_full.find('div', class_='jobsearch-JobMetadataHeader-item')
        if job_metadata != None:
            job_wage = job_metadata.find('span',class_='icl-u-xs-mr--xs')
            job_offer = job_metadata.find('span',class_='jobsearch-JobMetadataHeader-item icl-u-xs-mt--xs')
            if job_wage != None:
                job_wage_s = str(job_wage.text)
                print(job_wage_s)
            else:
                write_log('\n(!) job_wage not found')
                write_log(str(job_metadata))
            if job_offer != None:
                job_offer_s = str(job_offer.text)
                print(job_offer_s)
            else:
                write_log('\n(!) job_offer not found')
#                write_log(str(job_metadata))
        else:
            write_log('\n(!) job_metadata not found')
#            write_log(str(job_full))
        #
        # Grabbing company raiting and number of reviews
        job_company_rating_f = 0.0
        job_company_reviews_n = 0
        job_company_rating = job_full.find('meta', {'itemprop':'ratingValue'})
        job_company_reviews = job_full.find('meta', {'itemprop':'ratingCount'})
        if job_company_rating != None:
            job_company_rating_f = float(job_company_rating['content'])
            print(job_company_rating_f)
        if job_company_reviews != None:
            job_company_reviews_n = int(job_company_reviews['content'])
            print(job_company_reviews_n)
        #
        # Check if job exist in DB, add if it doesn't, insert it in the DB
        now = datetime.now()
        cursor = cnx.cursor()
        cursor.execute('select count(*) from jobs where ' + \
                       'title="' + job_title_s + '" and company="' + job_company_s + '" and location_main="' + job_location_main_s + '"')
        job_check = cursor.fetchone()
        if job_check[0] == 0:
            write_log(job_description_s)
            sql = "insert into jobs (title, company, location_main, location, wage, offer, summary, description, \
                                     easily_apply, urgently_hiring, link, company_rating, company_reviews, status, \
                                     submission_date) \
                              values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            val = (job_title_s, job_company_s, job_location_main_s, job_location_s, job_wage_s, job_offer_s, \
                   job_summary_s, job_description_s, job_easily_apply_s, job_urgently_hiring_s, job_link_s, \
                   job_company_rating_f, job_company_reviews_n, 'New', now.strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute(sql, val)
    #
    # Close DB connection
    cnx.commit()
    cursor.close()
    cnx.close()

now = datetime.now()
write_log(now.strftime("[%Y-%m-%d] [%H:%M:%S] Starting..."))

URL = 'https://www.indeed.com/jobs?as_and=&as_phr=&as_any=&as_not=clearence+clearance+SCI+DOD+TS%2FSCI&as_ttl=devops&as_cmp=&jt=all&st=&as_src=&salary=&radius=25&l=&fromage=1&limit=50&sort=date&psf=advsrch&from=advancedsearch'
#URL = 'https://www.indeed.com/jobs?as_and=&as_phr=&as_any=&as_not=clearence+clearance+SCI+DOD+TS%2FSCI&as_ttl=devops&as_cmp=&jt=all&st=&as_src=&salary=&radius=25&l=&fromage=7&limit=50&sort=date&psf=advsrch&from=advancedsearch'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
job_list = soup.find(id='resultsCol')
job_list_blocks = job_list.find_all('div', class_='jobsearch-SerpJobCard unifiedRow row result', limit=0)
extract_jobs(job_list_blocks)
print('Page 1\n')

page_list = soup.find('div', class_='pagination')
if page_list != None:
    page_list_blocks = page_list.findAll('a')
    for page_list_block in page_list_blocks:
        time.sleep(1)
        if page_list_block.find('span', class_='np') == None:
            page_list_url_s = str(page_list_block['href'])
            page = requests.get('https://indeed.com' + page_list_url_s)
            soup = BeautifulSoup(page.content, 'html.parser')
            job_list = soup.find(id='resultsCol')
            job_list_blocks = job_list.findAll('div', class_='jobsearch-SerpJobCard unifiedRow row result', limit=0)
            extract_jobs(job_list_blocks)
            print('Next page\n')
