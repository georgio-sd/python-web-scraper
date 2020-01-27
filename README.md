# Indeed web scraper (with BeautifulSoup library)
This python script scrapes unique(!) jobs from indeed.com and puts them into MySQL DB. 
Then users can process the job offers they pulled locally. It saves job seekers' time because they do not need to read hundreds repetitive offers, which indeed shows them every time when employers pushed their offers on top of the list.
* indeed-scraper.py - backend script, loads job offers to the database
* index.py - frontend script, user interface
* update.py - frontend script, marks job offers as applied, not interested or will check later
* database-table - MySQL (MirandaDB) database structure

Description https://youtu.be/2L7bsxUteyE
