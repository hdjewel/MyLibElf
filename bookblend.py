from flask import Flask, render_template, redirect, request, flash
from sqlalchemy import desc
import model

app = Flask(__name__)


@app.route("/", methods=["GET"])
def get_user_login():
    # I need to get the user login information from the login.html file
    return render_template("login.html")

@app.route("/", methods=["POST"])
def process_user_login():
    user_email = request.form.get("email")
    user_password = request.form.get("password")

    if str(user_email) == '' or str(user_password) == '':
        flash("Please enter a valid email and password.", "error")
        return render_template("login.html")

    else:
        user = model.session.query(model.User).filter_by(email = user_email).first()

        if user is None:
            # new_user = model.User(email = user_email, password = user_password)
            # model.session.add(new_user)
            # model.session.commit()
            # add the user to the data base
            # this is where I would add the user_email and user_password to the Users table
            # print "%s : %s" % (new_user.email, new_user.password)
            # return redirect("/user_list")
            print "The email / password can not be found. Please enter a valid email and password."
            return render_template("login.html")
        else:

            if user.password != user_password:
                print "password entered does not match the value on the table"
                return render_template("login.html")
            else:
                return redirect("/user_list")

@app.route("/user_list")
def user_list():
    user_list = model.session.query(model.User).limit(15).all()
    return render_template("user_list.html", users=user_list)
    # the actual "thing" containing the list of users queried from the DB is users
        
@app.route("/user/<int:id>")
def ratings(id):
    rating_list = (model.session.query(model.Rating)
                                .join(model.Movie).filter(model.Rating.user_id==id)
                                .order_by(model.Movie.name)
                                .all())
    # SELECT * FROM ratings INNER JOIN movies ON (ratings.movie_id=movies.id) WHERE user_id=5
    # ORDER BY movie_rating, name
    return render_template("user.html", user_id=id, ratings=rating_list)

if __name__ == "__main__":
    app.run(debug = True)
