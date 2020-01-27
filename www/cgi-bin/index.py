#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################################
# Indeed job scraper v0.2 (front end, web interface)
# Jan 21 2020
################################################################################################

import mysql.connector
from mysql.connector import errorcode

def print_header():
    print('''
<!DOCTYPE html>
<html>
<head>
  <title>Work site</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
 
  <style>
  * {
    box-sizing: border-box;
}
body {
    margin:0;
    padding: 0;
    width: 100%;
    font-size: 16px;
    color: #000;
        background: #eee;
}
a {
    text-decoration: none;
    color: #000;
}
img {
    vertical-align: middle;
}
 
.work-full > div:not(.item1) {
    display: none;
}
.work-tabs {
    display: flex;
    justify-content: space-between;
    flex-flow: row wrap;
    padding: 20px;
}
 
.work-preview {
    width: 30%;
    height: calc(100vh - 100px);
    overflow: auto;
}
.work-preview::-webkit-scrollbar {width:0px;}
.work-full {
    width: 68%;
}
.work-preview-item {
    padding: 15px;
    background: #fff;
    margin-bottom: 5px;
    cursor: pointer;
}
.work-preview-item:last-child {
    margin-bottom: 0;
}
.work-full-item {
    background: #fff;
    height: calc(100vh - 100px);
    padding: 15px;
    overflow: auto;
}
.vac-name {
    font-weight: bold;
    font-size: 22px;
    margin-bottom: 10px;
}
.vac-name a {
    font-weight: bold;
    font-size: 22px;
    color:#000;
}
.vac-btn-block {
    text-align: center;
    margin: 20px 0;
}
.vac-btn-block a {
    display: inline-block;
    vertical-align: top;
    border: 2px solid #eee;
    border-radius: 20px;
    padding: 10px 40px;
    text-transform: uppercase;
}
.vac-btn-block a:hover {
    background: #eee;
}
.work-preview-item .vac-price {
    margin-top: 20px;
}
.work-preview-item.active-item {
    -webkit-box-shadow: inset 0px 0px 5px 0px rgba(0,0,0,0.75);
    -moz-box-shadow: inset 0px 0px 5px 0px rgba(0,0,0,0.75);
    box-shadow: inset 0px 0px 5px 0px rgba(0,0,0,0.75);
}
@media screen and (max-width:910px){
    .work-tabs{
        display:block;
    }
    .work-preview {
        width: 100%;
        display: flex;
        height:auto;
    }
    .work-preview-item {
        width: 100%;
        min-width: 300px;
        border: 2px solid #eeee;
        margin: 0;
    }
    .work-full{
        width: 100%;
    }
    .work-full-item{
        height:auto;
    }
}
@media screen and (max-width:768px){
    .vac-btn-block a {
        width: 100%;
        margin-bottom: 15px;
    }
}
@media screen and (max-width:500px){
.work-tabs {
 
        padding: 10px;
}
}


  </style>
  <script>
      jQuery(document).ready(function($) {
          $(".work-preview-item").click(function(){

              var $current = $('.work-preview-item.active-item');
              $current.removeClass('active-item');

              $(this).addClass('active-item');

              class_1 = $(this).attr('data-for');
              $(".work-full-item").hide();
              $(".work-full-item."+class_1).show().animate({scrollTop:0},50);

          });
          $(".confirm-btn, .cancel-btn, .later-btn").click(function(){
              param = $(this).attr('param');
              $.get("/cgi-bin/update.py?"+param, function (data){
                 console.log(data);
              });

          });
      });
  </script>


</head>
''')

def print_file(file_name):
    f = open(file_name, "r")
    file_content = f.read()
    f.close()
    print(file_content)

def get_jobs():
    try:
        cnx = mysql.connector.connect(user='js', password='*****',
                                      host='localhost', database='job_scraper')
    except mysql.connector.Error as err:
        import sys
        sys.exit(err)

    cursor = cnx.cursor()
    cursor.execute('select * from jobs where status="New";')
    jobs = cursor.fetchall()
    cursor.close()
    cnx.close()
    return jobs

jobs = get_jobs()

print_header()

print('<body>')
print('<div class="wrapp">')
print('<div class="work-tabs">')
print('<div class="work-preview">')

i = 0
for row in jobs:
    i = i + 1
    job_id = row[0]
    job_title = row[1]
    job_company = row[2]
    job_location_main = row[3]
    job_location = row[4]
    job_wage = row[5]
    job_offer = row[6]
    job_summary = row[7]
    job_description = row[8]
    job_easily_apply = row[9]
    job_urgently_hiring = row[10]
    job_link = row[11]
    job_company_rating = row[12]
    job_company_reviews = row[13]
    job_status = row[14]
    job_submission_date = row[15]
    if i==1:
        print('<div class="work-preview-item item' + str(i) + ' active-item" data-for="item' + str(i) + '">')
    else:
        print('<div class="work-preview-item item' + str(i) + '" data-for="item' + str(i) + '">')
    print('<div class="vac-name">' + job_title + '</div>')
    if str(job_company_rating) != '0.0':
        print('<div class="vac-company"><b>' + job_company + '</b> *' + str(job_company_rating) + '</div>')
    else:
        print('<div class="vac-company"><b>' + job_company + '</b></div>')
    print('<div class="vac-city">' + job_location_main + '</div>')
    print('<div class="vac-price">' + job_wage + job_offer + '</div>')
    if job_easily_apply=='Y' and job_urgently_hiring=='Y':
        print('<div class="vac-info">Easily Apply - Urgently hiring</div>')
    elif job_easily_apply == 'Y' and job_urgently_hiring != 'Y':
        print('<div class="vac-info">Easily Apply</div>')
    elif job_easily_apply != 'Y' and job_urgently_hiring == 'Y':
        print('<div class="vac-info">Urgently hiring</div>')
    else:
        print('<div class="vac-info"></div>')
    print('<div class="vac-short-desc">' + job_summary + '</div>')
    print('</div>')
print('</div>')

print('<div class="work-full">')
i = 0
for row in jobs:
    i = i + 1
    job_id = row[0]
    job_title = row[1]
    job_company = row[2]
    job_location_main = row[3]
    job_location = row[4]
    job_wage = row[5]
    job_offer = row[6]
    job_summary = row[7]
    job_description = row[8]
    job_easily_apply = row[9]
    job_urgently_hiring = row[10]
    job_link = row[11]
    job_company_rating = row[12]
    job_company_reviews = row[13]
    job_status = row[14]
    job_submission_date = row[15]
    print('<div class="work-full-item item' + str(i) + '">')
    print('<div class="vac-name"><a href="' + 'https://www.indeed.com' + job_link + '" target="_blank">' \
          + job_title + '</a></div>')
    if str(job_company_rating) != '0.0':
        print('<div class="vac-company"><b>' + job_company + '</b> ' + str(job_company_rating) + ' – ' \
              + str(job_company_reviews) + ' &nbsp;&nbsp;' + job_location + '</div>')
    else:
        print('<div class="vac-company"><b>' + job_company + '</b> &nbsp;&nbsp;' + job_location + '</div>')
    print('<div class="vac-price">' + job_wage + job_offer + '</div>')
    if job_easily_apply=='Y' and job_urgently_hiring=='Y':
        print('<div class="vac-info">Easily Apply - Urgently hiring</div>')
    elif job_easily_apply == 'Y' and job_urgently_hiring != 'Y':
        print('<div class="vac-info">Easily Apply</div>')
    elif job_easily_apply != 'Y' and job_urgently_hiring == 'Y':
        print('<div class="vac-info">Urgently hiring</div>')
    else:
        print('<div class="vac-info"></div>')
    print('<div class="vac-id">ID = ' + str(job_id) + '</div>')
    print('<div class="vac-btn-block">')
    print('<a href="#" param="id=' + str(job_id) + '&status=AP" class="confirm-btn">Applied</a>')
    print('<a href="#" param="id=' + str(job_id) + '&status=NI" class="cancel-btn">Not interested</a>')
    print('<a href="#" param="id=' + str(job_id) + '&status=CL" class="later-btn">Will check later</a>')
    print('</div>')
    print('<div class="vac-full-desc">' + job_description + '</div>')
    print('</div>')
print('</div>')

print('</div>')
print('</div>')
print('</body>')
print('</html>')
