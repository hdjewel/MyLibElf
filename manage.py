""" This module manage.py is the server module that handles all the call, 
      put, and post request for the web app.                              """
from flask import Flask, render_template, redirect, request, flash
from sqlalchemy import desc
import itertools
import model
import pybookshare
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

        return render_template('login.html')

@app.route('/', methods=['POST'])
def process_patron_login():
    patron_email = request.form.get('email')
    patron_password = request.form.get('password')

    patron = check_for_patron(model.db_session, patron_email)
    if patron is None:
        return render_template('login.html')
    else:
        return redirect('/main')

    ### for testing only

    # if str(patron_email) == '' or str(patron_password) == '':
    #     flash('Please enter a valid email and password.', 'error')
    #     return render_template('login.html')

    # else:
    #     patron = model.db_session.query(model.Patron).filter_by(email=patron_email).first()
    #     if patron is None:
    #         print 'The email / password can not be found. Please enter a valid email and password.'
    #         return render_template('login.html')
    #     else:

    #         if patron.password != patron_password:
    #             print 'password entered does not match the value on the table'
    #             return render_template('login.html')
    #         else:
    #             log_the_patron_in(patron)                
    #             return redirect('/index')
#end app.route

@app.route('/main')
def main():
    return render_template('index.html')
#end app.route

@app.route('/library')
def library():
    setup_libraries_info(model.db_session, patron)
    return render_template('library.html')
#end app.route

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
#end app.route

@app.route('/process_search')
def search_results():
    x = request.args.get('source')
    print "source == ", x
    patron_login_id ='dvemstr'
    new_row = get_finished_books(patron_login_id)

#    get_bookshare_books(search_criteria)



    return render_template('book_list.html', books=new_row)
    # return render_template('book_list.html')
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
    patron = check_for_patron(model.db_session, patron_email)

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

def check_for_patron(db_session, patron_email):
    patron = (model.db_session.query(model.Patron)
                .filter_by(email = patron_email).first())
    return patron
#end def

def get_finished_books(patron_login_id):
    search_result = (model.db_session.query(model.Finished_Book,
                                         model.Book,
                                         model.Book_Author,
                                         model.Author)
                                   .filter(model.Finished_Book.book_id == model.Book.id,
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
    new_row = []
    for book_id, result_set in books_grouped_by_id:

        # r[3] in the result_set is the author object.

        # print book_id, ", ".join(r[3].name for r in result_set)

        for d in result_set:
            # new_row += [(str(d[1].title), str(d[0].date), str(d[3].name),
            #           str("".join(r[3].name for r in result_set)))]
            # new_row += [(d[1].title, d[0].date, d[3].name,
            # print "name = ", d[3].name
            new_row += [(d[1].title, d[0].date, d[3].name,
                      "".join(r[3].name for r in result_set))]
    # print "new row == ", new_row


    # print search_result

    # print "Calling source of this route / function is == ", x
    # search_result = (model.db_session.query(model.Book)
    #                              .join(model.Book_Author)
    #                              .join(model.Author)
    #                              .order_by(model.Book.title).limit(15).all())
    # print "search_result contains == " , search_result
    # for book_author in search_result:
    #     print "author found ", book_author.author.name
    #     print "date found ", book_author.book.finished_book.date
    return new_row
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

def setup_libraries_info(db_session, patron):
    pass

#end def

def get_bookshare_user_info(patron):


    print "this still needs to be coded."
    return username

#end def

def get_bookshare_books(search_criteria):
    """ The following commands work in python to return 3 book per page from
     the Bookshare API
    BS_API_KEY=   ==> get from ENV variable
    bs_url='https://api.bookshare.org/book/search/author/kellerman/page/1/limit/3/format/json?api_key=BS_API_KEY'
    results = requests.post(bs_url)
    results
    results.text
    """

    # no matter how the books are retreived a new_row array of books
    #  must be created
    return new_row
#end def

def log_the_patron_in():
    print 'redirect to /index'
    return redirect('/index')
#end def

if __name__ == '__main__':
    app.run(debug = True)