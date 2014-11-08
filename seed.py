import model   # if you do it this way, model.Patron, model.connect
import csv
import sys
from model import Book, Patron, Author
from datetime import datetime
import re

def import_read_books(session):

    filename = './seed_data/booklist.csv'

    print (0, "file name = ", filename)

    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter ='\t')
        try:
            for row in reader:
                # print "each row = ", row
                if row[0] == 'ISBN-10':
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
                    print "what is in book id after a add =", book.id
                    author = Author(
                        name=main_author
                        )
                    session.add(author)
                    print "what is in book id after a main author add =", author.id
                    # author_book = Author_Book(
                    #     author_id=author.id
                    #     book_id=book.id
                    #     )
                    # session.add(author_book)
                    author = Author(
                        name=sub_author
                        )
                    session.add(author)
                    print "what is in author id after a sub author add =", author.id
                    # author_book = Author_Book(
                    #     author_id=author.id
                    #     book_id=book.id
                    #     )
                    # session.add(author_book)
                #end if

            #end for            
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))   
#end def

def parse_book_title(title):
    title = re.sub('\(\d+\)', '', title).rstrip()
    title = title.decode("latin-1")
    
    return title
#end def

def import_patron(session):

    filename = './seed_data/u.item'
    
    print (0, "file name = ", filename)

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

def main(session):
    import_read_books(session)
    # import_patron(session)

    session.commit()
#end def

if __name__ == "__main__":
    s= model.connect()
    main(s)
