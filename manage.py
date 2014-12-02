""" This route manage.py is the server module that handles all the call, 
      put, and post request for the web app.  

"""
from flask import Flask, render_template, redirect, request, flash, session
from flask import Blueprint
from flask.ext.paginate import Pagination
import requests
from sqlalchemy import desc
import itertools
import model
from local_settings import APP_SECRET_KEY
import overdrive_apis
import booksearch
import json

# for salting passwords use os.urandom
"""
The following security logic will be implemented if this app ever is used by 
    persons other than the original developer.

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
app.secret_key=APP_SECRET_KEY

mod = Blueprint('books', __name__)

@app.route("/", methods=['GET'])
def get_patron_login():
    """ This app route displays the login page 

    """
    return render_template('login.html')
#end app.route
 
@app.route('/', methods=['POST'])
def process_patron_login():
    """ This route allows the patron to log into the app if their 
         information is configured in the database.

    """
    error = None
    patron_email = request.form.get('email')
    patron_password = request.form.get('password')

    patron = model.check_for_patron(model.db_session, 
                                    patron_email, 
                                    patron_password)

    if patron is None:
        flash("Please enter a valid email and password.")
        error = "Invalid credentials"
        return render_template('login.html', error=error)
    else:
        session['logged_in'] = True
        session['patron'] = patron.id
        session['fname'] = patron.fname
    #end if

    return redirect('/main')

#end app.route

@app.route('/overdrive_login')
def redirect_to_overdrive_url():
    """ This route gets the patron_access_token from OverDrive after the patron
         "logs into" the library using OverDrive Oauthentication.

         The level of access this app has is for the OverDrive integration 
          system and this app does not have the authority from OverDrive to
          access patron information yet.
    """
    from local_settings import OD_API_CLIENT_KEY

    # od_url_clientid = OD_API_CLIENT_KEY
    # od_url_redirect_uri = "http://localhost:5000/oauth_overdrive"
    # od_url_accountId = '4425'   """ Library id -- should be a passed parameter"""
    # od_url_state = 'turtlebutt'
    # od_url = 'https://oauth.overdrive.com/auth?'
    # od_url = od_url + 'clientid=' + od_url_clientid
    # od_url = od_url + '&redirect_uri=' + od_url_redirect_uri
    # od_url = od_url + '&scope=accountId:' + od_url_accountId
    # od_url = od_url + '&response_type=code&state=' + od_url_state 

    # print "Overdrive url = ", od_url, "\n"
    """ This is the url to the OverDrive integration test system 

    """
    od_url = 'https://oauth.overdrive.com/auth?clientid=LORETTAPOWELL&redirect_uri=http://localhost:5000/oauth_overdrive&scope=accountId:4425&response_type=code&state=turtle'
    # od_url = 'https://berkeleyca.libraryreserve.com/10/50/en/SignIn.htm?URL=SignOutConfirm%2ehtm'
    return redirect(od_url)

@app.route('/oauth_overdrive')
def process_overdrive_response():
    """ This route will be used by the OverDrive APIs to redirect the patron's 
         when they have closed the external OverDrive library login screen.

    """

    print "in process_overdrive response", "\n"
    session['patron_access_token'] = requests.args.get("code")
    print "patron access token = ", session['patron_access_token'], "\n"
    if requests.args.get("state") != 'turtle':
        flash(" Patron Access Token comprimised!")
    
    return redirect('/library')

    """
    {redirectUri}?code={authorizationCode}[&state={optionalStateParameter}
    """

@app.route('/main')
def main():
    """ This route displays the main/index page.

    """
    return render_template('index.html')
#end app.route

@app.route('/library', methods=['GET'])
def display_library_info():
    """ This route gets the list of libraries and displays the list.

    """
    print "in display library info \n"
    library_list = model.get_libraries_info(model.db_session, session)
    return render_template('library.html', libraries=library_list)
#end app.route

@app.route('/add_library', methods=['POST'])
def process_add_library():
    """ This route allows the patron to add libraries to the app.

    """
    print "in route add_library \n"

    library_fields = []
    library_name = request.form.get('libraryname')
    library_card_nbr = request.form.get('librarycardnbr')
    library_pin = request.form.get('librarypin')
    library_url = request.form.get('url')
    library_fields = (library_name, library_card_nbr, library_pin,  library_url)
    if (library_name == "" or library_card_nbr == "" 
    or library_pin == "" or library_url == ""):
        flash("Please enter all four fields: Library name, card number, " + 
            "pin and Library URL.")
    else:
        library = model.check_for_library(model.db_session, 
                                        library_card_nbr)

        if library is None:
            model.add_library(model.db_session, library_fields)
        fLash('The library was successfully added.')
        #end if
    #end if
    return redirect('/library')

#end app.route

@app.route('/logout')
def logout():
    """ This route logs the patron off the app.

    """
    session.pop('logged_in', None)
    session.pop('fname', None)
    session.pop('patron', None)
    flash('You were logged out')
    return redirect('/')
#end app.route

@app.route('/process_books_read_by_patron')
def get_books_read_by_patron():
    """ This route get all the "finished reading" books for a given patron and 
         displays the list of books.
    """
    search = False
    if session['patron']:
        search = False
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    list_of_books = model.get_finished_books(session['patron'])

    pagination = Pagination(page=page, 
                            total=len(list_of_books), 
                            search=search, 
                            record_name='list_of_books')
    return render_template('finished_book_list.html',
                           list_of_books=list_of_books,
                           pagination=pagination,
                           )
#end app.route

@app.route('/process_books_read')
def get_books_read():
    """ This route gets the list of books in the "finished reading" data set
         for the given search criteria and displays it.

    """
    search = False
    if session['patron']:
        search = False
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    search_criteria = request.args.get('search')
    if search_criteria == "":
        list_of_books = []
        pagination = Pagination(page=page, 
                        total=len(list_of_books), 
                        search=search, 
                        record_name='list_of_books')

        flash("Please enter an author or a title.")

        return render_template('finished_book_list.html',
                           list_of_books=list_of_books,
                           pagination=pagination,
                           )
    else:
        print "get a selection of books"
        list_of_books = model.get_finished_books_by_criteria(search_criteria, 
                                                             session['patron'])

        pagination = Pagination(page=page, 
                                total=len(list_of_books), 
                                search=search, 
                                record_name='list_of_books')

        return render_template('finished_book_list.html',
                               list_of_books=list_of_books,
                               pagination=pagination,
                               )
#end app.route

@app.route('/get_checked_outs')
def get_checked_outs():
    """ This route is calls white box OverDrive module that is being used
         because the patron_access_token is not yet available to this app.
    
         This white box route will return a list as if the remote library 
          had been accessed.
    """
    no_token = 'Y'
    list_of_books = overdrive_apis.get_list_of_checkouts(no_token)
    return render_template('hold_list.html', list_of_books=list_of_books, what='checkout')   
#end app.route

@app.route('/process_checked_outs')
def check_out_book():
    """ This route is calls the black box OverDrive module that is being used
         because the patron_access_token is not yet available to this app.
    """
    book = request.form
    success_code = overdrive_apis.checkout_book(book)
    flash('The book was successfully checked out and is ready to be downloaded.')
    return render_template('book_details.html', list_of_books=book, what='checkout')
#end app.route

@app.route('/process_checked_ins')
def check_in_book():
    """ This route is calls the black box OverDrive module that is being used
         because the patron_access_token is not yet available to this app.
    """
    book = request.form
    success_code = overdrive_apis.checkin_book(book)
    flash('The book was successfully checked in and is ready to be downloaded.')
    return render_template('book_details.html', list_of_books=book, what='checkout')
#end app.route

@app.route('/get_wish_lists', methods=["GET"])
def get_wish_lists():
    """ OverDrive does not yet provide an API to retrieve books on patron's
         wish list.
    """
    flash("The Wish list feature is under construction! Please check back soon!")
    return render_template('index.html')
#end app.route

@app.route('/process_wish_lists')
def put_on_wish_list():
    """ OverDrive does not yet provide an API to retrieve books on patron's
         wish list.
    """
    book = request.form
    flash("The Wish list feature is under construction! Please check back soon!")
    return render_template('book_details.html', list_of_books=book)
#end app.route

@app.route('/get_hold_lists', methods=["GET"])
def get_hold_lists():
    """ This route is calls white box OverDrive route that is being used
         because the patron_access_token is not yet available to this app.
    
         This white box module will return a list as if the remote library 
          had been accessed.
    """
    no_token = 'Y'
    list_of_books = overdrive_apis.get_hold_list(no_token)
    return render_template('hold_list.html', list_of_books=list_of_books, what='hold')
#end app.route

@app.route('/process_hold_lists')
def put_on_hold():
    """ This route is calls the black box OverDrive route that is being used
         because the patron_access_token is not yet available to this app.
    """
    book = request.form
    print "book from request.form in process_hold_lists = ", book, "\n"
    success_code = overdrive_apis.put_book_on_hold(book)
    flash('The book was successfully put on hold.')
    return render_template('book_details.html', list_of_books=book, what='hold')
#end app.route

@app.route('/process_suggestions')
def get_suggestions():
    """ This route would get the 'recommendations' from the Libraries 
         configured with OverDrive and display the list.
    """

    flash("The Recommendation feature is under construction! Please check back soon!")
    return render_template('index.html')
#end app.route

@app.route('/process_search')
def search_results():
    """ This module gets the search criteria from the form and calls the 
         external search modules to get lists of books to then display.

    """
    search = False
    if session['patron']:
        search = False
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    search_criteria = request.args.get('search')
    patron_id = session['patron']
    session['search_criteria'] = search_criteria

    if search_criteria != '':
        print "do a search"
        list_of_books = booksearch.search(search_criteria, patron_id)
        pagination = Pagination(page=page, 
                                total=len(list_of_books), 
                                search=search, 
                                record_name='list_of_books')
        return render_template('book_list.html', search=search_criteria,
                                list_of_books=list_of_books,
                                pagination=pagination,
                               )
    else:
        flash("Please enter an author or a title.")
        return render_template('index.html')

#end app.route
@app.route("/book_details", methods=["POST"])
def show_book():
    """This page shows the details of a given book, as well as giving an
    option to put the book on hold, on a wish list, or check out"""
    book = request.form
    print "book from request.form in show_book = ", book, "\n"
    return render_template("book_details.html",
                  book = book)
#end app.route

@app.route('/patron', methods=['GET'])
def display_patron():
    patron_fields = model.get_patron_info(session['patron'])
    return render_template('patron.html', patron_fields=patron_fields)
#end app.route

@app.route('/patron', methods=['POST'])
def process_changes_to_patron_info():
    patron_fields = {}
    patron_fields['id'] = session['patron']
    patron_fields['email'] = request.form.get('email')
    patron_fields['fname'] = request.form.get('fname')
    patron_fields['lname'] = request.form.get('lname')
    patron_fields['cell'] = request.form.get('cell')
    flash_msg = model.update_patron(model.db_session, patron_fields)
    flash(flash_msg)
    return render_template('patron.html', patron_fields=patron_fields)
#end app.route

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')
#end app.route

@app.route('/register', methods=['POST'])
def process_register():
    patron_fields = []

    patron_email = request.form.get('email')
    patron_password = request.form.get('password')
    patron_fname = request.form.get('fname')
    patron_lname = request.form.get('lname')
    patron_cell = request.form.get('phone')
    patron_fields = (patron_email, patron_password, patron_fname, patron_lname,
                    patron_cell)
    if (patron_email == "" or patron_password == "" 
    or patron_fname == "" or patron_cell == ""):
        flash("Please enter all 5 fields: Email address, Password, " + 
            "First and Last name, and Cell phone number.")
        return render_template('register.html')
    else:
        patron = model.check_for_patron(model.db_session, 
                                        patron_email, 
                                        patron_password)

        if patron is None:
            model.add_patron(model.db_session, patron_fields)
            return redirect('/')
        #end if
    #end if
#end app.route

@app.route('/get_password', methods=['GET'])
def get_password():
    return render_template('forgot_password.html')
#end app.rounte

@app.route('/forgot_password',methods=['POST'])
def forgot_password():
    # code logic to send password to an email account
    flash('An email will be sent with instructions on how to change your password')
    return redirect('/')
#end app.route

def get_bookshare_user_info(patron):
    """ not sure if getting information from Bookshare adds to this app. The 
         only checkouts and 1 month history of checkouts.
    """
    pass

#end def

def log_the_patron_in():
    print 'redirect to /index'
    return redirect('/index')
#end def

if __name__ == '__main__':
    app.run(debug = True)