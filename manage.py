""" This module manage.py is the server module that handles all the call, 
      put, and post request for the web app.                              """
from flask import Flask, render_template, redirect, request, flash, session
import requests
from sqlalchemy import desc
import itertools
import model
# from local_settings import BS_API_KEY
import overdrive_apis
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

""" test of api calls """
@app.route('/token', methods=['POST'])
def test_api():
    print "\n headers == ", request.headers
    print "\n data == ", request.values
#end def


@app.route("/", methods=['GET'])
def get_patron_login():
    """ This app route displays the login page 

    """
    return render_template('login.html')
#end app.route
 
@app.route('/', methods=['POST'])
def process_patron_login():
    error = None
    response = None #need this definition of response because it's first used in an 'else' block.
    patron_email = request.form.get('email')
    patron_password = request.form.get('password')

    patron = model.check_for_patron(model.db_session, 
                                    patron_email, 
                                    patron_password)
    # print "entered email = ", patron_email
    # print "password = ", patron_password
    # print "\n\n"
    # print "patron = ", patron

    if patron is None:
        flash("Please enter a valid email and password.", "error")
        return render_template('login.html')
    else:
        # print "patron id = ", patron.id
        # print "patron password = ", patron.password
        session['logged_in'] = True
        session['patron'] = patron.id
        session['fname'] = patron.fname
        # print "session --> ", session
        # print "first name == ", patron.fname
        print "session dictionary === ", session, "\n"
        response, response_data = overdrive_apis.log_into_overdrive()
        print response_data
    #end if

    """ Add logic to handle any response in the post_response_data other
         than the success code of 200.

    """
    print response.status_code, "  ==  ", response.reason
    if response.status_code > 201:
        flash(("Action was not successful. %s == %s\n") % 
                (response.status_code, response.reason))
        return render_template('login.html')
    elif response.status_code == 200:
        return redirect('/main')
        client_credentials = response.content
    elif response.status_code == 201:
        print "Post to get access token was successful"
        return redirect('/main')

    #end if

#end app.route

@app.route('/overdrive_login')
def redirect_to_overdrive_url():
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
    od_url = 'https://oauth.overdrive.com/auth?clientid=LORETTAPOWELL&redirect_uri=http://localhost:5000/oauth_overdrive&scope=accountId:4425&response_type=code&state=turtlebutt'
    return redirect(od_url)

@app.route('/oauth_overdrive')
def process_overdrive_response():

    session['patron_access_token'] = requests.args.get("code")
    if requests.args.get("state") != 'turtlebutt':
        flash(" Patron Access Token comprimised!")
    
    return redirect('/library')

    """
    {redirectUri}?code={authorizationCode}[&state={optionalStateParameter}
    """

@app.route('/main')
def main():
    return render_template('index.html')
#end app.route

@app.route('/library', methods=['GET'])
def display_library_info():
    print "in route library \n"
    library_list = model.setup_libraries_info(model.db_session, session)
    return render_template('library.html', libraries=library_list)
#end app.route

@app.route('/add_library', methods=['POST'])
def process_add_library():
    print "in route add_library \n"

    library_fields = []

    library_name = request.form.get('libraryname')
    library_card_nbr = request.form.get('librarycardnbr')
    library_pin = request.form.get('librarypin')
    library_url = request.form.get('url')
    library_fields = (library_name, library_card_nbr, library_pin,  library_url)
    print "library row after join -- ", library_fields, "\n"
    print "library card nbr = ", library_card_nbr, "\n"
    library = model.check_for_library(model.db_session, 
                                    library_card_nbr)

    # for n in library:
    print library.name
    print library.card_nbr
    print library.pin
    print library.url

    if library is None:
        model.add_library(model.db_session, library_fields)
    
    return redirect('/library')

#end app.route

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('fname', None)
    session.pop('patron', None)
    flash('You were logged out')
    return redirect('/')
#end app.route

@app.route('/process_books_read_by_patron')
def get_books_read_by_patron():

    list_of_books = model.get_finished_books(session['patron'])
    return render_template('finished_book_list.html', 
                            list_of_books=list_of_books)
#end app.route

@app.route('/process_books_read')
def get_books_read():

    search_criteria = request.args.get('search')
    print "search == ", search_criteria
    if search_criteria == "":
        flash("Please enter a Key word(s), author, or title.")
        return render_template('finished_book_list.html')
    else:
        print "get a selection of books"
        list_of_books = model.get_finished_books_by_criteria(search_criteria, 
                                                             session['patron'])
    return render_template('finished_book_list.html', 
                            list_of_books=list_of_books)
  
#end app.route

@app.route('/process_checked_outs')
def get_checked_outs():

    flash("The Check out process is under construction! Please check back soon!")
    return render_template('index.html')
#end app.route

@app.route('/process_wish_lists')
def get_wish_lists():

    flash("The Wish list feature is under construction! Please check back soon!")
    return render_template('index.html')
#end app.route

@app.route('/process_hold_lists')
def get_hold_lists():

    flash("The Hold list feature is under construction! Please check back soon!")
    return render_template('index.html')
#end app.route

@app.route('/process_suggestions')
def get_suggestions():

    flash("The Recommendation feature is under construction! Please check back soon!")
    return render_template('index.html')
#end app.route

@app.route('/process_search')
def search_results():
    search_criteria = request.args.get('search')
    print "search == ", search_criteria
    if search_criteria != '':
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
    else:
        flash("Please enter a Key word(s), author, or title.")
        return render_template('index.html')

#end app.route
@app.route("/book_details/<int:book>")
def show_book(book):
    """This page shows the details of a given book, as well as giving an
    option to put the book on hold, on a wish list, or check out"""
    return render_template("book_details.html",
                  display_book = book)

#end app.route

@app.route('/patron', methods=['GET'])
def display_patron():
    print session
    patron_fields = model.get_patron_info(session['patron'])
    print '\n patron fields = \n', patron_fields
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
    # print "patron row after join -- ", patron_fields
    patron = model.check_for_patron(model.db_session, 
                                    patron_email, 
                                    patron_password)

    if patron is None:
        model.add_patron(model.db_session, patron_fields)
        return redirect('/')
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

    print "this still needs to be coded."
    return username

#end def

def log_the_patron_in():
    print 'redirect to /index'
    return redirect('/index')
#end def

if __name__ == '__main__':
    app.run(debug = True)