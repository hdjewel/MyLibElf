""" This module model.py defines the database structure to be used by
      by SQLAlchemy to build and interact with the databse.           """
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session


engine = create_engine("sqlite:///bookblend.db", echo=True)

session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))
Base = declarative_base()

Base.query = session.query_property()

### Begin Class declarations

class Author(Base):
    """docstring for Author"""
    __tablename__ = "authors"

    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = True)
    fname = Column(String(40), nullable = True)
    lname = Column(String(40), nullable = True)

    # booksauthors = relationship("Book_Author")   [BA, BA, Ba[]]
    books = relationship("Book", secondary="books_authors")  #[B, B, B]

class Biblio(Base):
    """docstring for Biblio"""
    __tablename__ = "biblios"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    date = Column(Date, nullable = True)

class Book(Base):
    """docstring for Book"""
    __tablename__ = "books"
    
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

    # bookauthors = relationship("Book_Author")
    authors = relationship("Author", secondary="books_authors")
    libraries = relationship("Book_Library")
    finished_book = relationship("Finished_Book", uselist=False, backref='book')

class Checked_Out_Book(Base):
    """docstring for Checked_Out_Book"""
    __tablename__ = "checked_out_books"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    date = Column(Date, nullable = True)

class Finished_Book(Base):
    """docstring for Finished_Book"""
    __tablename__ = "finished_books"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    date = Column(Date, nullable = True)

class Hold(Base):
    """docstring for Hold"""
    __tablename__ = "holds"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    date = Column(Date, nullable = True)

class Library(Base):
    """docstring for Library"""
    __tablename__ = "libraries"

    id = Column(Integer, primary_key = True)
    name = Column(String(40), nullable = True)
    url = Column(String(40), nullable = True)
    card_nmbr = Column(Integer, nullable = True)
    pin = Column(Integer, nullable = True)
    login_id = Column(String(32), nullable = True)
    password = Column(String(18), nullable = True)

class Patron(Base):
    """docstring for Patron"""
    __tablename__ = "patrons"

    id = Column(Integer, primary_key = True)
    fname = Column(String(40), nullable = True)
    lname = Column(String(40), nullable = True)
    login_id = Column(String(32), nullable = True)
    password = Column(String(64), nullable = True)
    email = Column(String(64), nullable = True)
    cell = Column(String(10), nullable = True)

    notes = relationship("Book_Patron_Note")
    libraries = relationship("Patron_Library")

class Wish(Base):
    """docstring for Wish"""
    __tablename__ = "wish"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    date = Column(Date, nullable = True)

class Book_Author(Base):
    """docstring for Book_Author"""
    __tablename__ = "books_authors"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable = False)

    book = relationship("Book", backref=backref("books_authors", order_by=id))
    author = relationship("Author", backref=backref("books_authors", order_by=id))

class Book_Library(Base):
    """docstring for Book_Library"""
    __tablename__ = "books_libraries"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable = False)

    book = relationship("Book", backref=backref("books_libraries", order_by=id))
    library = relationship("Library", backref=backref("books_libraries", order_by=id))

class Book_Patron_Note(Base):
    """docstring for Book_Patron_Note"""
    __tablename__ = "books_patrons_notes"

    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    note = Column(String(4000), nullable = True)

    book = relationship("Book", backref=backref("books_patrons_notes", order_by=id))
    patron = relationship("Patron", backref=backref("books_patrons_notes", order_by=id))

class Patron_Library(Base):
    """docstring for Patron_Library"""
    __tablename__ = "patrons_libraries"

    id = Column(Integer, primary_key = True)
    patron_id = Column(Integer, ForeignKey('patrons.id'), nullable = False)
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable = False)

    patron = relationship("Patron", backref=backref("patrons_libraries", order_by=id))
    library = relationship("Library", backref=backref("patrons_libraries", order_by=id))

### End Class declarations

### Begin Function definitions

def connect():

    ENGINE = create_engine("sqlite:///bookblend.db", echo=False)
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