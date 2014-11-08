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

### Class declarations go here
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

class Author(Base):
    """docstring for Author"""
    __tablename__ = "authors"

    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = True)
    # fname = Column(String(40), nullable = True)
    # lname = Column(String(40), nullable = True)
    books = relationship("Author_Book")

class Author_Book(Base):
    """docstring for Author_Book"""
    __tablename__ = "authors_books"
    id = Column(Integer, primary_key = True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable = False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable = False)

    author = relationship("Author", backref=backref("authors_books", order_by=id))
    book = relationship("Book", backref=backref("authors_books", order_by=id))

### End class declarations
def connect():

    ENGINE = create_engine("sqlite:///bookblend.db", echo=True)
    Session = sessionmaker(bind=ENGINE)
    Base.metadata.create_all(ENGINE)

    return Session()

def main():
    pass
    # return session

if __name__ == "__main__":
    main()
