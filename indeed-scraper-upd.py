#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################################
# Indeed job scraper v0.6 (back end)
# Jan 12 2020
################################################################################################
import requests
import re
import time
import mysql.connector
import hashlib
from mysql.connector import errorcode
from datetime import datetime
from bs4 import BeautifulSoup

# Write to the log file, for debugging
def write_log(data):
    log_file = open(r"/root/python/webscraper/ws.log","a")
    log_file.write(data + '\n')
    log_file.close()

# Additional filters, which filter jobs with the patterns in title and location
def job_filter(job_title, job_location):
    def isIn(ps, st):
        for p in ps:
            if re.search(p, st):
                return True
        return False
    title_patterns = ['SR\.', 'SR ', 'SENIOR', 'LEAD', 'PRINCIPAL', 'MANAGER', 'DIRECTOR', 'STAFF',
                      'SOFTWARE ENGINEER', 'SOFTWARE DEVELOPER', 'AZURE', 'INTERN', 'JAVA']
    location_patterns = ['NEW YORK', 'BOSTON', 'CAMBRIDGE', 'SAN FRANCISCO', 'SAN JOSE']
    if isIn(title_patterns, job_title.upper()) or isIn(location_patterns, job_location.upper()):
        return 'FL'
    return 'New'

def load_hash():
    try:
        cnx = mysql.connector.connect(user='js', password='cbbctsnpzs',
                                      host='localhost', database='job_scraper')
    except mysql.connector.Error as err:
        import sys
        sys.exit(err)
    cursor = cnx.cursor()
    cursor.execute('select id, group_concat(hash) from hashes group by id;')
    hash_list_bulk = cursor.fetchall()
    cursor.close()
    cnx.close()
    hash_list = []
    for i in hash_list_bulk:
        hash_list.append([i[0], [int(n) for n in i[1].split(',')]])
    return hash_list

# Extracting jobs from an html page
def extract_jobs(job_list_blocks):
    #
    # Converting text to a hash list
    def words_hash(text):
        #removing all html tags
        text = re.sub('<.*?>', ' ', text)
        #replacing all non alphabetical characters with spaces
        text = re.sub('[^a-z]', ' ', text.lower())
        #removing all words with less than 3 letters and extra spaces
        normal_text = ' '.join(wrd for wrd in text.split() if len(wrd)>2)
        words = normal_text.split()
        i = len(words)
        n = 0
        hashes = []
        while n <= i-3:
            st = words[n] + words[n+1] + words[n+2]
            hashes.append(int(hashlib.sha256(st.encode('utf-8')).hexdigest(), 16) % 10**19)
            n = n + 1
        hashes.sort()
        return list(dict.fromkeys(hashes))
    #
    # Checking if a job description is unique
    def hash_check(hash_list, job_hash, percent):
        for hashes in hash_list:
            pr = len(set(hashes[1]) & set(job_hash))*100/((len(hashes[1]) + len(job_hash))/2)
            if pr >= percent:
                write_log('Found ' + str(round(pr)) +  '% double in DB with ID=' + str(hashes[0]))
                return False
        return True

    global hash_list_global
##    try:
##        cnx = mysql.connector.connect(user='js', password='cbbctsnpzsr',
##                                      host='localhost', database='job_scraper')
##    except mysql.connector.Error as err:
##        import sys
##        sys.exit(err)
    added_jobs = 0
    processed_jobs = 0
    added_new_jobs = 0
    for job_list_block in job_list_blocks:
        #
        # Grabbing a job title and a link
        processed_jobs = processed_jobs + 1
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
        # Grabbing a company name
        job_company = job_list_block.find('span', class_='company')
        if job_company != None:
            job_company_s = str(job_company.text)
        else:
            job_company_s = 'Unknown'
            write_log('\n(!) job_company not found')
            write_log(str(job_list_block))
        job_company_s = job_company_s.strip()
        #
        # Grabbing a main location
        job_location_main = job_list_block.find('div', class_='recJobLoc')
        if job_location_main != None:
            job_location_main_s = str(job_location_main['data-rc-loc'])
        else:
            job_location_main_s = ''
            write_log('\n(!) job_location_main not found')
            write_log(str(job_list_block))
        job_location_main_s = job_location_main_s.strip()
        #
        # Grabbing an extra location
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
        #
        # Grabbing a job summary
        job_summary = job_list_block.find('div', class_='summary')
        if job_summary != None:
            job_summary_s = str(job_summary)
            job_summary_s = re.sub(' style=".*?"', '', job_summary_s)
            job_summary_s = re.sub('<div class="metadataDiv">.*</div>', '</div>', job_summary_s)
            if len(job_summary_s) > 400:
                write_log(job_title_s)
                write_log(job_company_s)
                write_log(job_summary_s)
        else:
            job_summary_s = ''
            write_log('\n(!) job_summary not found')
            write_log(str(job_list_block))
        job_summary_s = job_summary_s.strip()
        #
        # Checking if a job exists in the DB
##        cursor = cnx.cursor()
##        cursor.execute('select count(*) from jobs where title="' + job_title_s + '" and \
##                        company="' + job_company_s + '" and location_main="' + job_location_main_s + '";')
##        job_check = cursor.fetchone()
        if (0 == 0):
            #
            # Parsing a job page
            # Grabbing a job description
            #time.sleep(0.2)
            page = requests.get('https://www.indeed.com' + job_link_s)
            soup = BeautifulSoup(page.content, 'html.parser')
            job_full = soup.find('div', class_='jobsearch-JobComponent icl-u-xs-mt--sm')
            if job_full != None:
                job_description = job_full.find('div', class_='jobsearch-jobDescriptionText')
            else:
                write_log('\n(!) job_full not found')
                write_log(job_title_s)
                write_log(job_company_s)
                write_log(job_link_s)
                write_log(str(soup))
            if job_description != None:
                job_description_s = str(job_description)
            else:
                job_description_s = ''
                write_log('\n(!) job_description not found')
                write_log(str(job_full))
            #
            # Grabbing a wage and an offer
            job_wage_s = ''
            job_offer_s = ''
            job_metadata = job_full.find('div', class_='jobsearch-JobMetadataHeader-item')
            if job_metadata != None:
                job_wage = job_metadata.find('span',class_='icl-u-xs-mr--xs')
                job_offer = job_metadata.find('span',class_='jobsearch-JobMetadataHeader-item icl-u-xs-mt--xs')
                if job_wage != None:
                    job_wage_s = str(job_wage.text)
                if job_offer != None:
                    job_offer_s = str(job_offer.text)
            #
            # Grabbing a company raiting and a number of reviews
            job_company_rating_f = 0.0
            job_company_reviews_n = 0
            job_company_rating = job_full.find('meta', {'itemprop':'ratingValue'})
            job_company_reviews = job_full.find('meta', {'itemprop':'ratingCount'})
            if job_company_rating != None:
                job_company_rating_f = float(job_company_rating['content'])
            if job_company_reviews != None:
                job_company_reviews_n = int(job_company_reviews['content'])
            #
            # Calculating description hash
            job_hash = words_hash(job_description_s)
            added_jobs = added_jobs + 1
            #
            # Applying the filteres
            job_status_s = job_filter(job_title_s, job_location_main_s)
##            if job_status_s == 'New':
                #
                # Checking if a job is unique, we accept less than 80% of similarity
##                if hash_check(hash_list_global, job_hash, 80):
##                    added_new_jobs = added_new_jobs + 1
##                    write_log('[New] - ' + job_title_s + ' (' + job_location_main_s + ')')
##                else:
##                    write_log('[Double] - ' + job_title_s + ' (' + job_location_main_s + ')')
##                    job_status_s = 'DBL'
##            else:
##                write_log('[Filtered] - ' + job_title_s + ' (' + job_location_main_s + ')')
            #
            # Saving a job to the DB
            now = datetime.now()
            sql = "insert into jobs (title, company, location_main, location, wage, offer, summary, description, \
                                     easily_apply, urgently_hiring, link, company_rating, company_reviews, status, \
                                     submission_date) \
                              values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            val = (job_title_s, job_company_s, job_location_main_s, job_location_s, job_wage_s, job_offer_s, \
                   job_summary_s, job_description_s, job_easily_apply_s, job_urgently_hiring_s, job_link_s, \
                   job_company_rating_f, job_company_reviews_n, job_status_s, now.strftime("%Y-%m-%d %H:%M:%S"))
##            cursor.execute(sql, val)
            print(val);
            #
            # Saving a description hash to the DB and add to the hash_list_global variable
##            cursor.execute('select LAST_INSERT_ID();')
##            last_id = cursor.fetchone()
##            hash_list_global.append([last_id[0], job_hash])
##            for hs in job_hash:
##                cursor.execute('insert into hashes values(LAST_INSERT_ID(), ' + str(hs) + ');')
    #
    # Closing DB connection
##    cnx.commit()
##    cursor.close()
##    cnx.close()
    return (added_jobs, processed_jobs, added_new_jobs)
#
# Writing start event to the log file
started_time = datetime.now()
write_log(started_time.strftime("\n[%Y-%m-%d] [%H:%M:%S] Starting..."))
print(started_time.strftime("Started at [%H:%M:%S]...\n"))
##hash_list_global = load_hash()
#
# Requesting the first page
#URL = 'https://www.indeed.com/jobs?as_and=&as_phr=&as_any=&as_not=clearence+clearance+SCI+DOD+TS%2FSCI&as_ttl=devops&as_cmp=&jt=all&st=&as_src=&salary=&radius=25&l=&fromage=2&limit=50&sort=date&psf=advsrch&from=advancedsearch'
URL = 'https://www.indeed.com/jobs?as_and=&as_phr=&as_any=&as_not=clearence+clearance+SCI+DOD+TS%2FSCI&as_ttl=devops&as_cmp=&jt=all&st=&as_src=&salary=&radius=25&l=&fromage=2&limit=50&sort=date&psf=advsrch&from=advancedsearch&filter=0'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
job_list = soup.find(id='resultsCol')
job_list_blocks = job_list.find_all('div', class_='jobsearch-SerpJobCard unifiedRow row result', limit=0)
(added_jobs, processed_jobs, added_new_jobs) = extract_jobs(job_list_blocks)
print('Page 1 has been parsed,')
print('Jobs processed: ' + str(processed_jobs))
print('Jobs added    : ' + str(added_jobs))
print('Jobs to check : ' + str(added_new_jobs) + '\n')
parsed_pages = 1
#
# Checking if there are more pages to parse
page_list = soup.find('div', class_='pagination')
if page_list != None:
    page_list_blocks = page_list.findAll('a')
    if len(page_list_blocks) == 2:
        print(str(len(page_list_blocks) - 1) + ' more page was found\n')
    else:
        print(str(len(page_list_blocks) - 1) + ' more pages were found\n')
    for page_list_block in page_list_blocks:
        #time.sleep(0.2)
        if page_list_block.find('span', class_='np') == None:
            page_list_url_s = str(page_list_block['href'])
            page = requests.get('https://www.indeed.com' + page_list_url_s)
            soup = BeautifulSoup(page.content, 'html.parser')
            job_list = soup.find(id='resultsCol')
            job_list_blocks = job_list.findAll('div', class_='jobsearch-SerpJobCard unifiedRow row result', limit=0)
            (i, n, x) = extract_jobs(job_list_blocks)
            processed_jobs = processed_jobs + n
            added_jobs = added_jobs + i
            added_new_jobs = added_new_jobs + x
            parsed_pages = parsed_pages + 1
            print('Page ' + str(parsed_pages) + ' has been parsed,')
            print('Jobs processed: ' + str(n))
            print('Jobs added    : ' + str(i))
            print('Jobs to check : ' + str(x) + '\n')

finished_time = datetime.now()
time_diff = finished_time - started_time
print('>>> Total info <<<')
print('Pages parsed  : ' + str(parsed_pages))
print('Jobs processed: ' + str(processed_jobs))
print('Jobs added    : ' + str(added_jobs))
print('Jobs to check : ' + str(added_new_jobs))
print('Speed         : ' + str(round(processed_jobs / time_diff.total_seconds(), 2)) + ' (job/sec)')
print(finished_time.strftime("\nFinished at [%H:%M:%S]"))
write_log(finished_time.strftime("[%Y-%m-%d] [%H:%M:%S] Finished"))
