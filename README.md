# MyLibElf
### Hackbright Final Project

===========

## Introduction

Accessing multitude of library systems one at a time is very time consuming and labor intensive, 
MyLibElf streamlines the patron’s process by accessing these libraries, and combining the libraries’ 
search responses into one search result. The search results can be refined to see the patron’s Hold 
and Checked Out lists. 

MyLibElf, also contains a repository of books a patron has read and imported into the MyLibElf database. This 
allows real-time information to assist in deciding to check out a book or not. 

MyLibElf currently configured to allows one user to access 3 libraries - San Francisco Public Library, 
BookShare.org, and the OverDrive Integration Library.

**Note:** Once OverDrive approves this application for their production libraries, MyLibElf will only be limited by 
the number of library cards a person has to libraries that use OverDrive to manage their books*

## Table of Contents
- [Introduction](#introduction)
- [Searching for a book to read](#Searching for a book to read)
- [Configuring Libraries](#Configuring Libraries)
- [Logging into MyLibElf](#Logging into MyLibElf)
- [Importing Data](#Importing Data)
- [Technologies used](# Technologies used)
- [Installation](#installation)

## Searching for a book to read

The main page offers two ways to look for a book.  Choices include looking into books alread ready and searching
external libraries. The main page offers options to manage books in a patron's external library accounts.
As well as ways to manage the MyLibElf patron information and to configure libraries.

![Main Page Screen]
(/screen_shots/Main_Page_Screen.png)

Selecting "Books you've read" causes the MyLibElf data base to be accessed and books the patron has imported will 
retrieved and displayed.

![Finished]
(/screen_shots/Finished_Screen.png)

Entering an Author or Title into the search field will cause an external query on all the configured libraries. 
Using a scraping method on the HTML from one library using PyQuery and AJAX calls to APIs on the other two 
libraries. The search results are combined and displayed.

![Search Results Page 1]
(/screen_shots/Top_Of_Search_Page_Screen.png)
![Search Results Page 2]
(/screen_shots/Bottom_of_Search_Page_Screen.png)

If the book has details (usually from the OverDrive libraries), the title can be click and using JavaScript the 
details are displayed.

![Book Detail Screen]
(/screen_shots/Book_Detail_Screen.png)

##Configuring Libraries

Also from the main page, patrons can add new libraries to search.

![Library Configuration Screen]
(/screen_shots/Library_Configuration_Screen.png)

##Logging into MyLibElf

MyLibElf is a multi-patron app. The login page has links to manage patron access for both old and new patron who
want use MyLibElf to save time and energy.

![Login Screen]
(/screen_shots/Login_Screen.png)

##Importing Data

MyLibElf uses a Sqlite3 data base to save book data. To import data into the data set for already read books, a
text file must be created. The format for this data file is:

  ISBN-10, ISBN-13, ISBN Number, Barcode Nbr, Main Author, Sub Author, Title
  
Note: Only the Main Author and Title fields are required.

Once this file is created the seed.py program will read it and import the book information into the database.

## Technologies used

MylibElf uses a number of open source projects to work properly:

Python, Flask, Jinja2, Sqlite3, SQLAlchemy, JavaScript, JQuery, PyQuery, Requests, HTML/CSS, AJAX, Bookshare API, and OverDrive APIs.

## Installation

NOTE: Because the app requires Secret Keys and Tokens from OverDrive, it can not be independently installed. 

If new app keys and tokens are obtained from OverDrive, then the installation is as follows:
 
1. Get started by cloning this repo and installing all the required libraries:

	1. Create a python virtual environment::

	        virtualenv env


	2. Activate the virtual environment::

	        source env/bin/activate


	3. Install the requirements::

	        pip install -r requirements.txt

2. Next, set up SQLite (http://www.sqlite.org) according to the instructions on their site for your operating system.

3. Import the data filea and create the :

		python -i model.py 

	into your terminal. Then type the following line into your terminal to create the tables:

		Base.metadata.create_all(engine)

4. Edit API Client Key and API ACCESS KEY in the local_settings.py file to contain the keys obtained from OverDrive.

5. Run python manage.py in your terminal and send your browser to http://localhost:5000/

6. Select the "Create an Account" link on the login page to create a patron.

7. Create the data file of books to be imported into the database.

8. With your virtual environment activated, run seed.py {newly created login id}. (Do not type the "{}" when executing the seed.py program.)

7. Finally, use the newly created patron information to log into MyLibElf.

