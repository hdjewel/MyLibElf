""" This module manage.py is the server module that handles all the call, 
      put, and post request for the web app.                              """
from flask import Flask, render_template, redirect, request, flash, session
import requests
from sqlalchemy import desc
import itertools
import model
# from local_settings import BS_API_KEY
# import overdrive_apis
import booksearch

# for salting passwords use os.urandom
"""
To Store a Password

1 Generate a long random salt using a CSPRNG.
2 Prepend the salt to the password and hash it with a standard cryptographic hash 
function such as SHA256.
3 Save both the salt and the hash in the user's database record.

To Validate a Password

1 Retrieve the user's salt and hash from the database.
2 Prepend the salt to the given password and hash it using the same hash function.
3 Compare the hash of the given password with the hash from the database. If they 
match, the password is correct. Otherwise, the password is incorrect.

"""

app = Flask(__name__)
app.secret_key='\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'

@app.route("/", methods=['GET'])
def get_patron_login():
    """ This app route displays the login page 

    """
    return render_template('login.html')
#end app.route
 
@app.route('/', methods=['POST'])
def process_patron_login():
    error = None
    patron_email = request.form.get('email')
    patron_password = request.form.get('password')

    patron = check_for_patron(model.db_session, patron_email, patron_password)
    print "entered email = ", patron_email
    print "password = ", patron_password
    print "\n\n"
    print "patron = ", patron

    if patron is None:
        flash("Please enter a valid email and password.", "error")
        return render_template('login.html')
    else:
        print "patron id = ", patron.id
        print "patron password = ", patron.password
        session['logged_in'] = True
        session['patron'] = patron.id
        session['fname'] = patron.fname
        print "session --> ", session
        print "first name == ", patron.fname

        return redirect('/main')
#end app.route

@app.route('/main')
def main():
    return render_template('index.html')
#end app.route

@app.route('/library')
def library():
    library_list = setup_libraries_info(model.db_session, session)
    return render_template('library.html', libraries=library_list)
#end app.route

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect('/')
#end app.route

@app.route('/process_search')
def search_results():
    calling_link = request.args.get('source')
    search_criteria = request.args.get('search')
    print "calling link == ", calling_link
    print "search == ", search_criteria
    if search_criteria is not None and search_criteria != "":
        print "do a search"
        # list_of_books = search_for_books_by_criteria(search_criteria)
        list_of_books = booksearch.search(search_criteria)
        
        # for row in list_of_books:
        #   print "\n row = \n", row
        #   print "image = ", row['images'], 
        #   print "title = ", row['title'], 
        #   print "author = ", row['author'],
        #   print "available = ", row['availableToDownload']
        
        return render_template('book_list.html', search=search_criteria,
                                list_of_books=list_of_books)
    elif calling_link == 'booksRead':
        list_of_books = get_finished_books(session['patron'])
        return render_template('finished_book_list.html', list_of_book=list_of_books)
    elif calling_link == 'checkedOut':
        flash("The Check out process is under Construction! Please check back soon!")
        return render_template('index.html')
    elif calling_link == 'wishList':
        flash("The Wish list feature is under Construction! Please check back soon!")
        return render_template('index.html')
    elif calling_link == 'holdList':
        flash("The Hold list feature is under Construction! Please check back soon!")
        return render_template('index.html')
    elif calling_link == 'suggestion':
        flash("The Recommendation feature is under Construction! Please check back soon!")
        return render_template('index.html')
    else:
        flash("This link is under Construction! Please check back soon!")
        return render_template('index.html')

#end app.route
@app.route("/book_details/<int:book>")
def show_book(book):
    """This page shows the details of a given melon, as well as giving an
    option to put the book on hold, on a wish list, or check out"""
    return render_template("melon_details.html",
                  display_book = book)

#end app.route

@app.route('/process_search', methods=['POST'])
def delete_book():
    print "\nis this being called?\n"
    flash("This link is under Construction! Please check back soon!")
    return redirect('finished_book_list.html')

#end app.route

@app.route('/patron', methods=['GET'])
def display_patron():
    return render_template('patron.html')
#end app.route

@app.route('/patron', methods=['POST'])
def process_changes_to_patron_info():
    patron_fields = get_patron_info(session['patron_id'])
    print '\n patron fields = \n', patron_fields
    return render_template('patron.html', fields=patron_fields)
#end app.route

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')
#end app.route

@app.route('/register', methods=['POST'])
def process_register():
    patron_row = []

    patron_email = request.form.get('email')
    patron_password = request.form.get('password')
    patron_fname = request.form.get('fname')
    patron_lname = request.form.get('lname')
    patron_cell = request.form.get('phone')
    patron_row = (patron_email, patron_password, patron_fname, patron_lname,
                    patron_cell)
    print "patron row after join -- ", patron_row
    patron = check_for_patron(model.db_session, patron_email, patron_password)

    if patron is None:
        add_patron(model.db_session, patron_row)
        return redirect('/')
#end app.route

@app.route('/get_password', methods=['GET'])
def get_password():
    return render_template('forgot_password.html')
#end app.rounte

@app.route('/forgot_password',methods=['POST'])
def forgot_password():
    # code logic to send password to an email account
    return redirect('/')
#end app.route

def get_patron_info(patron_id):
    patron = (model.db_session.query(model.Patron)
                .filter(id = patron_id)
                .first())

    patron_fields = {}
    patron_fields['id'] = patron.id
    patron_fields['fname'] = patron.fname
    patron_fields['lname'] = patron.lname
    patron_fields['cell'] = patron.cell
    print "\n\n fields = ", patron_fields

    return patron_fields
#end def

def check_for_patron(db_session, patron_email, patron_password):
    patron = (model.db_session.query(model.Patron)
                .filter_by(email = patron_email, 
                        password = patron_password)
                .first())
    return patron
#end def

def get_finished_books(patron_id):
    search_result = (model.db_session.query(model.Finished_Book,
                                         model.Book,
                                         model.Book_Author,
                                         model.Author)
                                   .filter(model.Finished_Book.book_id == model.Book.id,
                                           model.Finished_Book.patron_id == patron_id,
                                           model.Book.id == model.Book_Author.book_id,
                                           model.Book_Author.author_id == model.Author.id)
                                   .order_by(model.Book.title).all())
    
    # for finished_book, book, book_author, author in search_result:
    #     print book.title
    #     print author.name
    #     print finished_book.date

    books_grouped_by_id = itertools.groupby(search_result, lambda x: x[1].id)
    # x[1] is the book object 
    # [ (1, [fb, b, ba, a]),
    #   (2, [fb, b, ba, a])]
    # where fb = finished_book
    #       b = book
    #       ba = book_author
    #       a = author
    list_of_books = []
    for book_id, result_set in books_grouped_by_id:

        # r[3] in the result_set is the author object.

        # print book_id, ", ".join(r[3].name for r in result_set)

        for d in result_set:
            # list_of_books += [(str(d[1].title), str(d[0].date), str(d[3].name),
            #           str("".join(r[3].name for r in result_set)))]
            # list_of_books += [(d[1].title, d[0].date, d[3].name,
            # print "name = ", d[3].name
            list_of_books += [(d[1].title, d[0].date, d[3].name,
                      "".join(r[3].name for r in result_set),
                      d[1].cover_png)]

    return list_of_books
#end def

def add_patron(db_session, patron_row):

    login_id, host = patron_row[0].split("@")
    new_patron = model.Patron(email = patron_row[0],
                              password = patron_row[1],
                              fname = patron_row[2],
                              lname = patron_row[3],
                              cell = patron_row[4],
                              login_id = login_id)
    db_session.add(new_patron)
    db_session.commit()

    print "in add_patron"
    print "\npatron_row = ", patron_row, "\n\n\n"
#end def

def setup_libraries_info(db_session, session):
    library_list = (model.db_session.query(model.Library)
                # .filterby(model.Patron_Library.patron == session['patron'],
                            # model.Library.id == model.Patron_Library.library_id)
                .all())
    print "\n library list \n", library_list
    return library_list

#end def

def get_bookshare_user_info(patron):


    print "this still needs to be coded."
    return username

#end def

# def search_for_books_by_criteria(search_criteria):
#     """ Search for books by the given search_criteria

#           Frist search Bookshare.org
#     """
#     list_of_books = get_bookshare_books(search_criteria)
#     # each subsequent call will add to this list of books

#     # This sorts the list of books "in place"
#     list_of_books.sort()
#     return list_of_books

# #end def

# def get_bookshare_books(search_criteria):
#     """ The following commands work in python to return 3 book per page from
#      the Bookshare API

#      """
#     bs_url=('https://api.bookshare.org/book/search/author/%s/page/1/limit/3/format/json?api_key=%s'
#         % (search_criteria, BS_API_KEY))
#     status = requests.get(bs_url)
#     print "\n\n"
#     print status
#     response_data = status.json()
#     list_of_books = response_data['bookshare']['book']['list']['result']
#     # The returned list of books are a dictionary of the following keys:
#     #
#     # publisher ,  isbn13 ,  author ,  availableToDownload ,  title , 
#     # briefSynopsis ,  dtbookSize ,  images ,  freelyAvailable ,  id ,
#     # downloadFormat
#     count = 0
#     print "data from the get = ", "\n"
#     for book in list_of_books:
#         if count < 2:
#             print book, "\n"
#             count = count + 1
#     print "\n\n"
    
#     return list_of_books
# #end def

def log_the_patron_in():
    print 'redirect to /index'
    return redirect('/index')
#end def

if __name__ == '__main__':
    app.run(debug = True)