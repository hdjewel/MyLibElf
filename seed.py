""" This module seed.py populates the data base with book titles from 
       a csv file.                                                    """
import model   # if you do it this way, model.Patron, model.connect
import csv
import sys
from model import Book, Patron, Author, Finished_Book, Note, connect
from datetime import datetime
import re

def import_read_books(db_session, patron, input_login_id):

    filename = './seed_data/test_books.txt'
    # filename = './seed_data/books.txt'
    # filename = './seed_data/booklist.csv'

    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter ='\t')
        try:
            for row in reader:
                """ Do not process header records.  
                """
                if row[0] == 'ISBN-10':
                    pass
                else:
                    """ Data file format is:
                        ISBN-10, ISBN-13, ISBN Number, Barcode Nbr, Main Author,
                         Sub Author, Title
                    """
                    data_ok = edit_imported_book_data(row)
                    if data_ok == True:

                        """ add logic to check if the book is already on the 
                            database and associated with this logon_id 

                            if book exists then just add finished_books and
                              notes.  """
                        book, patron = check_for_patron_book(db_session, 
                            input_login_id, row)
                        
                        print_stmt = ""
                        if book is None:
                            """ book """
                            book, main_author, sub_author = add_book(db_session, row)

                            """ main_author """
                            author = add_author(db_session, main_author)
                            book = add_book_author(db_session, book, author)

                            """ sub_author """
                            if sub_author == "" or sub_author == "N/A":
                                pass
                            else:
                                author = add_author(db_session, sub_author)
                                book = add_book_author(db_session, book, author)
                        else:
                            print_stmt = "The book %s already exists" % row[6]
                        #end if

                        # print "patron = ", patron
                        # print "dir of patron.Patron ===> ", patron.Patron
                        # print "patron.Patron.login_id =", patron.Patron.login_id

                        if patron is None:
                            """ finished """
                            book = add_finished_record_to_database(db_session, book,
                                                                    patron)

                            """ notes """
                            book = add_notes(db_session, book, patron)
                        else:
                            if print_stmt != "":
                                print_stmt = "%s for this patron %s" % (print_stmt, input_login_id)
                            else:
                                print_stmt = "Linked " + book.title 
                                print_stmt = print_stmt + " to " 
                                print_stmt = print_stmt + input_login_id
                            #end if
                        #end if
                        print print_stmt + "."
                    #end if
                #end if

            #end for            
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))   
#end def

def add_author(db_session, name):
    fname, lname = name.split()
    author = Author(
        name=name,
        fname=fname,
        lname=lname
        )
    db_session.add(author)
    db_session.flush()
    return author
#end def

def add_book(db_session, row):
    isbn_10, isbn_13, isbn, barcode_nbr, main_author, sub_author, title = row[0:]
    title = parse_book_title(title)
    date_added = datetime.now()

    book = Book(
        title=title,
        date_added=date_added,
        isbn=isbn,
        isbn_10 = isbn_10,
        isbn_13=isbn_13,
        barcode_nbr=barcode_nbr 
        )

    db_session.add(book)
    return book, main_author, sub_author
#end def

def add_book_author(db_session, book, author):
    # This is the logic to get data into the associative data set when
    #  the relationship is a many to many.
    # print "author - ", dir(author)
    # book_author = Book_Author()
    # print "dir of book_author  === ",
    # dir(book_author)
    # print"\n\n\n"
    # print "dir of book  === ",
    # dir(book)

    with db_session.no_autoflush:
        book.authors.append(author)
        # author.books.append(book_author)
    #end with
    db_session.add(book)
    return book
#end def

def add_finished_record_to_database(db_session, book, patron):
    # print "book.finished book = ", book.finished_book
    # print "\n\n dir of book ----> ", dir(book)
    # print "\n\n"
    # print "dir of book.patrons ---> ", dir(book.patrons)
    # print "\n book patron id === ", patron.id
    # print "\n\n\n"
    
    finished_book = Finished_Book()
    date = "2014-01-01"
    # print date
    finished_book.date = datetime.strptime(date, "%Y-%m-%d")
    finished_book.patron_id = patron.id

    with db_session.no_autoflush:
        book.finished_book = finished_book
    #end with
    db_session.add(book)
    return book
#end def

def add_notes(db_session, book, patron):
    note = Note()
    note.patron_id = patron.id
    with db_session.no_autoflush:
        book.notes.append(note)
    #end with
    db_session.add(book)
    return book
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

def check_for_patron_book(db_session, input_login_id, row):
    main_author = row[4]
    title = row[6]

    book = (model.db_session.query(model.Patron, model.Note, model.Book)
                .filter(model.Patron.login_id == input_login_id,
                        model.Patron.id == model.Note.patron_id,
                        model.Note.book_id == model.Book.id,
                        model.Book.title == title)
                .first())

    patron = (model.db_session.query(model.Patron, model.Note)
                .filter(model.Patron.login_id == input_login_id,
                        model.Patron.id == model.Note.patron_id)
                .first()) 

    return book, patron
#end def

def check_for_patron_login_id(db_session, input_login_id):
    patron = (model.db_session.query(model.Patron)
                .filter_by(login_id = input_login_id).first())

    return patron
#end def

def main(db_session, input_login_id):
    if input_login_id is None:
        print "A library patron's login id must be entered on the command line."
    else:
        patron = check_for_patron_login_id(db_session, input_login_id)

        if patron:
            import_read_books(db_session, patron, input_login_id)
            db_session.commit()
        else:
            print "The patron login id %s was not found in the database." % input_login_id
#end def

if __name__ == "__main__":
    db_session= connect()
    main(db_session, sys.argv[1])
