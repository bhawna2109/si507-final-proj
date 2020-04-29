# Hello there! Welcome to my SI507 final project
# Read Next

## Goal
This is a tool that'll help you finalize the next book that you should read and provide you with an option to preview the book.

## Data sources
This project surfaces data from:
- Goodreads
- Google Books

## Setup Instructions
To proceed, we will need you to create a secrets.py so that you can access goodreads API. This should look like:
GOODREADS_API_KEY = 'YourAPIKey'
GOODREADS_API_SECRET = 'YourAPISecret'

## Running the application
The "finalproj.py" will run the application

## Interactiong with the application
Once the program starts to run, the user should navigate to ""http://127.0.0.1:5000/" in a web browser. The interface will be your guide from there :)

### Interaction steps
- Enter a Goodreads ID in the textbox
- The program shows all the bookshelves that user has
- The user selects ONE bookshelf via a dropdown
- The program shows ALL the books in that bookshelf as a table. The user can use this table to compare books and decide which one to read. The user can also preview the book using the preview URL
- To read all reviews with a particular rating for a particular book, the user can choose the book and the rating from the dropdown. Clicking on the submit input type button will show all reviews in a new tab
- The user can click on a review URL to read full review on the Goodreads website
- The user can choose another book and rating pair to view all reviews for it

## Happy reading!


