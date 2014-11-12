""" This module seed.py populates the data base with book titles from 
       a csv file.                                                    """
import model   # if you do it this way, model.Patron, model.connect
import csv
import sys
from model import Book, Patron, Author, Book_Author, Finished_Book
from datetime import datetime
import re

def import_read_books(session):

    filename = './seed_data/test_books.txt'
    # filename = './seed_data/books.txt'
    # filename = './seed_data/booklist.csv'

    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter ='\t')
        try:
            for row in reader:
                """ Do not process header records.  """
                if row[0] == 'ISBN-10':
                    pass
                else:
                    data_ok = edit_imported_book_data(row)
                    if data_ok == True:
                        """ book """
                        book, main_author, sub_author = add_book(session, row)

                        """ main_author """
                        author = add_author(session, main_author)
                        add_book_author(session, book, author)

                        """ sub_author """
                        if sub_author == "" or sub_author == "N/A":
                            pass
                        else:
                            author = add_author(session, sub_author)
                            add_book_author(session, book, author)

                        """ finished """
                        add_finished_record_to_database(session, book)
                        #end if
                    #end if
                #end if

            #end for            
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))   
#end def

def add_author(session, name):
    author = Author(
        name=name
        )
    session.add(author)
    session.flush()
    return author
#end def

def add_book(session, row):
    isbn_10, isbn_13, isbn, barcode_nbr, main_author, sub_author, title = row[0:]
    title = parse_book_title(title)
    book = Book(
        isbn_10 = isbn_10,
        isbn_13=isbn_13, 
        isbn=isbn, 
        barcode_nbr=barcode_nbr, 
        title=title
        )
    session.add(book)
    return book, main_author, sub_author
#end def

def add_book_author(session, book, author):
    # This is the logic to get data into the associative data set when
    #  the relationship is a many to many.
    book_author = Book_Author()
    with session.no_autoflush:
        book.authors.append(book_author)
        author.books.append(book_author)
    #end with
    session.add(book)
#end def

def add_finished_record_to_database(session, book):
    finished_book = Finished_Book()
    date = "2014-01-01"
    finished_book.date = datetime.strptime(date, "%Y-%m-%d")
    with session.no_autoflush:
        book.finished_book.append(finished_book)
    #end with
    session.add(book)
    #end with
#end def

def edit_imported_book_data(row):
    cnt = 0
    for i in row:
        if i == "N/A":
            row[cnt] = ""
        #end if
        if cnt < 4:
            row[cnt] = re.sub('\s+', '-', row[cnt])
        #end if
        cnt = cnt + 1
    #end for
    return True
#end def

def parse_book_title(title):
    title = re.sub('\(\d+\)', '', title).rstrip()
    title = title.decode("latin-1")
    
    return title
#end def

"""
def import_patron(session):

    filename = './seed_data/u.item'

    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter ='|')
        try:
            for row in reader:
                first_name, last_name, logon_id, password, email, cell = row[0:]
                patron = Patron(
                    # id   ---- do I need this on the SQLAchemy call?
                    fname=first_name,
                    lname=last_name,
                    logon_id=logon_id,
                    password=password, 
                    email=email,
                    cell=cell
                    )
                session.add(patron)
            #end for
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))   
#end def
"""

def main(session):
    import_read_books(session)
    # import_patron(session)

    session.commit()
#end def

if __name__ == "__main__":
    s= model.connect()
    main(s)
