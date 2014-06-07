#This is just to test crawler using command line
##python test.py url count

import sys
from crawler import Crawler , Social

crawler_object=Crawler()
crawled_urls=list(set(crawler_object.crawl_start(sys.argv[1],sys.argv[2])))
print crawled_urls


social_object=Social()
social_counts=[]
for url in crawled_urls:
	social_counts.append(social_object.social_data(url))

print social_counts
