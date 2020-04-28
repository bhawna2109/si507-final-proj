import requests
# from bs4 import BeautifulSoup


url = "https://www.googleapis.com/books/v1/volumes"
params = {'q': "Harry Potter and the half blood"}

response = requests.get (url, params)
volumeID = response.json()["items"][0]["id"]

url1 = "https://www.googleapis.com/books/v1/volumes/"+volumeID
print(url1)
resp = requests.get(url1).json()

readerLink = resp["accessInfo"]["webReaderLink"]
print(readerLink)

# headers = {
#     'User-Agent': 'UMSI 507 Course Homework - Python Scraping and Crawling',
#     'From': 'bhawna@umich.edu',
#     'Course-Info': 'https://si.umich.edu/programs/courses/507'
# }
# url = "https://www.goodreads.com/book/show/23692271-sapiens"
# response = requests.get(url)
# resp = response.content

# soup = BeautifulSoup(resp, 'html.parser')
# all_list_items = soup.find_all('div', class_="review")
# print (all_list_items)

