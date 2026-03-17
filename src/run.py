import time

from crawler import scrape
from sitemap import create_sitemap

start= time.time()
url= input("Enter a url: ")
sitemap= create_sitemap(url)

result= scrape(sitemap)

end= time.time()
time_taken= end-start
print(result)

if time_taken <= 60:
    print(f'The time taken was: {time_taken} seconds')
else:
    print(f'The time taken was: {time_taken/60} minutes')