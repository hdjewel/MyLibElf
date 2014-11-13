""" This module manage.py is the server module that handles all the call, 
      put, and post request for the web app.                              """
from flask import Flask, render_template, redirect, request, flash
from sqlalchemy import desc
import itertools
import model

app = Flask(__name__)
app.secret_key='\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'

@app.route("/", methods=["GET"])
def get_patron_login():
        # I need to get the user login information from the login.html file
        return render_template("login.html")

@app.route("/", methods=["POST"])
def process_patron_login():
    patron_email = request.form.get("email")
    patron_password = request.form.get("password")
    
    ### for testing only 
    patron_email = "dvemstr@gmail.com"
    patron_password = 'dvetmp'
    patron_fname = "Isabel"
    patron_lname = "Ringing"
    log_the_patron_in()                
    return redirect("/main")

    ### for testing only

    # if str(patron_email) == '' or str(patron_password) == '':
    #     flash("Please enter a valid email and password.", "error")
    #     return render_template("login.html")

    # else:
    #     patron = model.session.query(model.Patron).filter_by(email=patron_email).first()
    #     if patron is None:
    #         print "The email / password can not be found. Please enter a valid email and password."
    #         return render_template("login.html")
    #     else:

    #         if patron.password != patron_password:
    #             print "password entered does not match the value on the table"
    #             return render_template("login.html")
    #         else:
    #             log_the_patron_in(patron)                
    #             return redirect("/index")
#end app.route

@app.route("/main")
def main():
    return render_template("index.html")
#end app.route

@app.route("/library")
def library():
    return render_template("library.html")
#end app.route

@app.route("/process_search")
def search_results():
    x = request.args.get("source")

    # search_result = (model.session.query(model.Book_Author)
    #                              .join(model.Book)
    #                              .join(model.Author)
    #                              .join(model.Finished_Book)
    #                              .order_by(model.Book.title).all())

    """can I create a variable called tables and assign model.Finished_Book,
        model.Book, model.Book_Author, model.Author to it , then use it in
        the query? This will allow me to use the query for all the searches.
        Maybe I do not need to do this.?????
    """
    search_result = (model.session.query(model.Finished_Book,
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
        # print book_id, result_set
        # r[3] in the result_set is the author object.

        # print book_id, ", ".join(r[3].name for r in result_set)

        for d in result_set:
            # new_row += [(str(d[1].title), str(d[0].date), str(d[3].name),
            #           str("".join(r[3].name for r in result_set)))]
            new_row += [(d[1].title, d[0].date, d[3].name,
                      "".join(r[3].name for r in result_set))]
    print "new row == ", new_row


    # print search_result

    # print "Calling source of this route / function is == ", x
    # search_result = (model.session.query(model.Book)
    #                              .join(model.Book_Author)
    #                              .join(model.Author)
    #                              .order_by(model.Book.title).limit(15).all())
    # print "search_result contains == " , search_result
    # for book_author in search_result:
    #     print "author found ", book_author.author.name
    #     print "date found ", book_author.book.finished_book.date
    return render_template("book_list.html", books=new_row)
    # return render_template("book_list.html")
#end app.route

@app.route("/register")
def register():
    return render_template("register.html")
#end app.route

def log_the_patron_in():
    print "redirect to /index"
    return redirect("/index")
#end def

"""
@app.route("/patron_list")
def patron_list():
    patron_list = model.session.query(model.patron).limit(15).all()
    return render_template("patron_list.html", patrons=patron_list)
    # the actual "thing" containing the list of patrons queried from the DB is patrons
        
@app.route("/patron/<int:id>")
def ratings(id):
    rating_list = (model.session.query(model.Rating)
                                .join(model.Movie).filter(model.Rating.patron_id==id)
                                .order_by(model.Movie.name)
                                .all())
    # SELECT * FROM ratings INNER JOIN movies ON (ratings.movie_id=movies.id) WHERE patron_id=5
    # ORDER BY movie_rating, name
    return render_template("patron.html", patron_id=id, ratings=rating_list)
"""

if __name__ == "__main__":
    app.run(debug = True)
