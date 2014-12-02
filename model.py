""" This module model.py defines the database structure to be used by
      by SQLAlchemy to build and interact with the databse.           """
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session
import itertools

engine = create_engine('sqlite:///bookblend.db', echo=True)

db_session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))
Base = declarative_base()

Base.query = db_session.query_property()

### Begin Class declarations

class Author(Base):
    """docstring for Author"""
    __tablename__ = "authors"

    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = True)
    fname = Column(String(40), nullable = True)
    lname = Column(String(40), nullable = True)

    booksauthors = relationship("Book_Author")  # [BA, BA, Ba[]]
    books = relationship('Book', secondary='books_authors')  #[B, B, B]

class Biblio(Base):
    """docstring for Biblio"""
    __tablename__ = "biblios"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    date = Column(Date, nullable = True)

    book = relationship('Book', backref=backref('biblios', order_by=id))

class Book(Base):
    """docstring for Book"""
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key = True)
    title = Column(String(120), nullable = True)
    cover_png = Column(String(200), nullable = True)
    date_added = Column(Date, nullable = True)
    isbn = Column(String(10), nullable = True)
    isbn_10 = Column(String(10), nullable = True)
    isbn_13 = Column(String(13), nullable = True)
    published_dt = Column(Date, nullable = True)
    genre = Column(String(50), nullable = True)
    barcode_nbr = Column(Integer, nullable = True)

    booksauthors = relationship("Book_Author")
    authors = relationship('Author', secondary='books_authors')
    # biblio = relationship('Book', uselist=False, backref='books')
    # checkedout = relationship('Book', uselist=False, backref='books')
    finished_book = relationship('Finished_Book', uselist=False, backref='books')
    # hold = relationship('Book', uselist=False, backref='books')
    libraries = relationship('Library', secondary='books_libraries')
    patrons = relationship('Patron', secondary='notes')
    # wish = relationship('Book', uselist=False, backref='books')
    
    def __str__(self):
        return "title: %s"%(self.title)

class Checkedouts(Base):
    """docstring for Checkedouts"""
    __tablename__ = 'checkedouts'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    date = Column(Date, nullable = True)

    book = relationship('Book', backref=backref('checkedouts', order_by=id))
    patron = relationship('Patron', backref=backref('checkedouts', order_by=id))

class Finished_Book(Base):
    """docstring for Finished_Book"""
    __tablename__ = 'finished_books'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    date = Column(Date, nullable = True)

    book = relationship('Book', backref=backref('finished_books', order_by=id))
    patron = relationship('Patron', backref=backref('nfinished_books', order_by=id))

class Hold(Base):
    """docstring for Hold"""
    __tablename__ = 'holds'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    date = Column(Date, nullable = True)

    book = relationship('Book', backref=backref('holds', order_by=id))
    patron = relationship('Patron', backref=backref('holds', order_by=id))
    
class Library(Base):
    """docstring for Library"""
    __tablename__ = 'libraries'

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = True)
    url = Column(String(255), nullable = True)
    access_token = Column(String(1000), nullable = True)
    card_nbr = Column(Integer, nullable = True)
    pin = Column(Integer, nullable = True)
    login_id = Column(String(255), nullable = True)
    password = Column(String(100), nullable = True)

    patronslibraries = relationship("Patron_Library")
    patrons = relationship('Patron', secondary='patrons_libraries')  #[B, B, B]

class Patron(Base):
    """docstring for Patron"""
    __tablename__ = 'patrons'

    id = Column(Integer, primary_key = True)
    fname = Column(String(40), nullable = True)
    lname = Column(String(40), nullable = True)
    login_id = Column(String(255), nullable = True)
    password = Column(String(100), nullable = True)
    email = Column(String(255), nullable = True)
    cell = Column(String(20), nullable = True)

    libraries = relationship('Library', secondary='patrons_libraries')
    books = relationship('Book', secondary='notes')  #[B, B, B]

class Wish(Base):
    """docstring for Wish"""
    __tablename__ = 'wishes'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    date = Column(Date, nullable = True)

    book = relationship('Book', backref=backref('wishes', order_by=id))
    patron = relationship('Patron', backref=backref('wishes', order_by=id))

class Book_Author(Base):
    """docstring for Book_Author"""
    __tablename__ = 'books_authors'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable = False)

    book = relationship('Book', backref=backref('books_authors', order_by=id))
    author = relationship('Author', backref=backref('books_authors', order_by=id))

class Book_Library(Base):
    """docstring for Book_Library"""
    __tablename__ = 'books_libraries'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable = False)

    book = relationship('Book', backref=backref('books_libraries', order_by=id))
    library = relationship('Library', backref=backref('books_libraries', order_by=id))

class Note(Base):
    """docstring for Note"""
    __tablename__ = 'notes'

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    note = Column(String(4000), nullable = True)

    book = relationship('Book', backref=backref('notes', order_by=id))
    patron = relationship('Patron', backref=backref('notes', order_by=id))

class Patron_Library(Base):
    """docstring for Patron_Library"""
    __tablename__ = 'patrons_libraries'

    id = Column(Integer, primary_key = True)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable = False)

    patron = relationship('Patron', backref=backref('patrons_libraries', order_by=id))
    library = relationship('Library', backref=backref('patrons_libraries', order_by=id))

### End Class declarations

### Begin Function definitions

def add_patron(db_session, patron_fields):

    login_id, host = patron_fields[0].split("@")
    new_patron = Patron(email = patron_fields[0],
                              password = patron_fields[1],
                              fname = patron_fields[2],
                              lname = patron_fields[3],
                              cell = patron_fields[4],
                              login_id = login_id)
    db_session.add(new_patron)
    db_session.commit()

    print "in add_patron"
    print "\npatron_fields = ", patron_fields, "\n\n\n"
#end def

def update_patron(db_session, patron_fields):

    print "fields are === ", patron_fields

    patron = Patron.query.filter_by(id=patron_fields['id']).first()

    if (patron.email == patron_fields['email']
    and patron.fname == patron_fields['fname']
    and patron.lname == patron_fields['lname']
    and patron.cell == patron_fields['cell']):
        flash_msg = "No change was made to your account information."
    else:
        """ Add the rest of the patron fields """
        patron.email = patron_fields['email']
        patron.fname = patron_fields['fname']
        patron.lname = patron_fields['lname']
        patron.cell = patron_fields['cell']
        db_session.commit()
        flash_msg = "Your account information was succesfully updated!"
    #end if
    return flash_msg
    print "after an update = ", patron_fields, "\n"
#end def

def check_for_patron(db_session, patron_email, patron_password):
    patron = (db_session.query(Patron)
                .filter_by(email = patron_email, 
                        password = patron_password)
                .first())
    return patron
#end def

def get_patron_info(patron_id):
    # print "patron id = ", patron_id, "\n"
    patron = (db_session.query(Patron)
                .filter_by(id=patron_id)
                .first())

    patron_fields = {}
    patron_fields['id'] = patron.id
    patron_fields['email'] = patron.email
    patron_fields['fname'] = patron.fname
    patron_fields['lname'] = patron.lname
    patron_fields['cell'] = patron.cell

    return patron_fields
#end def
def get_finished_books_by_criteria(search_criteria, patron_id):
    """
    change logic to select on search criteria
    """
    criteria = '%' + search_criteria + '%'
    search_result = (db_session.query(Finished_Book,
                                         Book,
                                         Book_Author,
                                         Author)
                                   .filter(Finished_Book.book_id == Book.id,
                                           Finished_Book.patron_id == patron_id,
                                           Book.id == Book_Author.book_id,
                                           Book_Author.author_id == Author.id,
                                           Book.title.like(criteria) |
                                           Author.name.like(criteria))
                                   .order_by(Book.title).all())    
    for finished_book, book, book_author, author in search_result:
        print book.title
        print author.name
        print finished_book.date
    #end for

    books_grouped_by_id = itertools.groupby(search_result, lambda x: x[1].id)

    list_of_books = []
    for book_id, result_set in books_grouped_by_id:


        for d in result_set:
            list_of_books += [(d[1].title, d[1].cover_png, d[0].date, d[3].name,
                      "".join(r[3].name for r in result_set))]
            print "new author field = ", d[3], "\n"
        #end for
    #end for

    return list_of_books

#end def

def get_finished_books(patron_id):
    search_result = (db_session.query(Patron,
                                      Library,
                                      Patron_Library)
                                   .filter(Patron.id == patron_id,
                                           Patron.id == Patron_Library.patron_id,
                                           Patron_Library.library_id == Library.id)
                                   .all())
    for patron, library, patron_library in search_result:
        print "List of Library = ", patron.id, patron.lname,
        print library.name, library.url
        print "\n"
    #end for

    search_result = (db_session.query(Finished_Book,
                                         Book,
                                         Book_Author,
                                         Author)
                                   .filter(Finished_Book.book_id == Book.id,
                                           Finished_Book.patron_id == patron_id,
                                           Book.id == Book_Author.book_id,
                                           Book_Author.author_id == Author.id)
                                   .order_by(Book.title).all())


    
    for finished_book, book, book_author, author in search_result:
        print book.title
        print author.name
        print finished_book.date
    #end for

    books_grouped_by_id = itertools.groupby(search_result, lambda x: x[1].id)
    list_of_books = []
    for book_id, result_set in books_grouped_by_id:

        for d in result_set:
            list_of_books += [(d[1].title, d[1].cover_png, d[0].date, d[3].name,
                      "".join(r[3].name for r in result_set))]
        #end for
    #end for

    return list_of_books
#end def

def get_patron_libraries(patron_id):

    search_result = (db_session.query(Patron,
                                      Library,
                                      Patron_Library)
                                   .filter(Patron.id == patron_id,
                                           Patron.id == Patron_Library.patron_id,
                                           Patron_Library.library_id == Library.id)
                                   .all())
    list_of_libraries = []
    for patron, library, patron_library in search_result:
        library_dict = {}

        library_dict['url'] = library.url
        library_dict['patron'] = patron_id
        library_dict['name'] = library.name
        library_dict['access_token'] = library.access_token
        print "library dictionary = ", library_dict, "\n"
        list_of_libraries.append(library_dict)
    #end for

    return list_of_libraries

#end def

def get_libraries_info(db_session, session):
    library_list = (db_session.query(Library)
                # .filterby(Patron_Library.patron == session['patron'],
                            # Library.id == Patron_Library.library_id)
                .all())
    print "in setup library info \n"
    return library_list

#end def

def check_for_library(db_session, library_card_nbr):
    print "in check for library \n"
    library = (db_session.query(Library)
                         .filter_by(card_nbr=library_card_nbr))

    return library
#end def

def add_library(db_session, library_fields):

    print "library fields = ", library_fields, "\n\n"
    new_library = Library(name = library_fields[0],
                         card_nbr = library_fields[1],
                         pin = library_fields[2],
                         url = library_fields[3])
    db_session.add(new_library)
    db_session.commit()

    print "in add_patron"
#end def

def connect():
    print "in connect"
    ENGINE = create_engine("sqlite:///bookblend.db", echo=True)
    Session = sessionmaker(bind=ENGINE)
    Base.metadata.create_all(ENGINE)

    return Session()

def main():
    pass

### End Function definitions 

### Begin Program

if __name__ == "__main__":
    main()

### End of Program