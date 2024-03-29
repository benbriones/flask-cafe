"""Flask App for Flask Cafe."""

import os

from flask import Flask, render_template, flash, redirect, url_for, session, g, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from models import connect_db, Cafe, db, City, DEFAULT_PROF_IMG_URL, User, DEFAULT_CAFE_IMG_URL, Like
from forms import AddEditCafeForm, SignUpForm, CSRFProtectForm, LoginForm, ProfileEditForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")

if app.debug:
    app.config['SQLALCHEMY_ECHO'] = True

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_form_to_g():
    """Add csrf protection"""

    g.csrf_form = CSRFProtectForm()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    GET: Show registration form
    POST: Process registration; if valid, adds user and then logs them in.
    if invalid, show form
    ”"""

    do_logout()
    form = SignUpForm()

    if form.validate_on_submit():
        user = User.register(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            description=form.description.data,
            email=form.email.data,
            password=form.password.data,
            image_url=form.image_url.data or None
        )

        db.session.add(user)

        try:

            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash('Username already taken', 'danger')
            return render_template('auth/signup-form.html', form=form)

        do_login(user)
        flash('You are signed up and logged in.', 'success')
        return redirect('/cafes')

    return render_template('auth/signup-form.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    GET: show login form
    POST: process login, if valid logs user in. If invalid,
    show login form
    """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data
        )

        if user:
            do_login(user)
            flash(f'Hello, {user.username}!', 'success')

            return redirect("/cafes")

        flash("Invalid credentials", 'danger')

    return render_template('/auth/login-form.html', form=form)


@app.post('/logout')
def logout():
    """logout user"""
    form = g.csrf_form

    if not form.validate_on_submit():
        return redirect("/")

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()
    flash("You've been successfully logged out!", "success")
    return redirect('/login')


#######################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/login')

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
    )


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/login')

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
    )


@app.route('/cafes/add', methods=["GET", "POST"])
def add_cafe():
    """
    GET: show form to add a cafe
    POST: handle form submission and add a cafe to DB
    """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/login')

    if not g.user.admin:
        flash("Unauthorized", "danger")
        return redirect("/")

    form = AddEditCafeForm()
    form.city_code.choices = City.get_choices()

    if form.validate_on_submit():
        cafe = Cafe(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            address=form.address.data,
            city_code=form.city_code.data,
            image_url=form.image_url.data or Cafe.image_url.default.arg
        )

        db.session.add(cafe)
        db.session.flush()
        cafe.save_cafe_map()


        db.session.commit()

        flash(f'{cafe.name} added!', "success")
        redirect_url = url_for('cafe_detail', cafe_id=cafe.id)
        return redirect(redirect_url)

    return render_template('cafe/add-form.html', form=form)


@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    """
    GET: show form to edit a cafe
    POST: handle form submission to edit a cafe
    """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/login')

    if not g.user.admin:
        flash("Unauthorized access", "danger")
        return redirect("/login")

    cafe = Cafe.query.get_or_404(cafe_id)
    old_address = cafe.address
    old_city = cafe.city_code

    form = AddEditCafeForm(obj=cafe)
    form.city_code.choices = City.get_choices()

    if form.validate_on_submit():
        form.populate_obj(cafe)

        changed_location = (
            old_address != form.address.data or
            old_city != form.city_code.data
            )

        if not form.image_url.data:
            cafe.image_url = Cafe.image_url.default.arg

        if changed_location:
            cafe.save_cafe_map()

        db.session.commit()


        flash(f'{cafe.name} edited!')
        redirect_url = url_for('cafe_detail', cafe_id=cafe.id)
        return redirect(redirect_url)

    # make it so relative isn't showed
    if cafe.image_url == Cafe.image_url.default.arg:
        form.image_url.data = ""

    return render_template('cafe/edit-form.html', form=form, cafe=cafe)

@app.post('/cafes/<int:cafe_id>/delete')
def delete_cafe(cafe_id):
    """Deletes cafe from database"""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect("/login")

    if not g.user.admin:
        flash("Unauthorized access", "danger")
        return redirect("/login")

    cafe = Cafe.query.get_or_404(cafe_id)

    if g.csrf_form.validate_on_submit():
        cafe.delete_cafe_map()

        db.session.delete(cafe)
        db.session.commit()

        flash('Cafe deleted', 'success')
        return redirect("/cafes")

    flash("Unauthorized access", "danger")
    return redirect("/login")


#########################
# user profiles

@app.get('/profile')
def display_user_profile():
    """Show user profile page."""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect("/login")

    return render_template('profile/detail.html')


@app.route('/profile/edit', methods=["POST", "GET"])
def edit_user():
    """
    GET: shows edit profile form
    POST: handle edit profile form submission
    """
    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect("/login")

    form = ProfileEditForm(obj=g.user)

    if form.validate_on_submit():
        form.populate_obj(g.user)

        g.user.image_url = form.image_url.data or DEFAULT_PROF_IMG_URL

        db.session.commit()

        flash('Profile edited.')
        return redirect(url_for('display_user_profile'))

    # so we don't have /static/images/default-pic.png as a default arg in form
    if g.user.image_url == User.image_url.default.arg:
        form.image_url.data = ""

    return render_template('/profile/edit-form.html', form=form)


#########################
# likes

@app.get('/api/likes')
def check_like():
    """
    Check if current user likes a speficifc cafe,returns
    JSON like: {"likes": true|false}
    """

    if not g.user:
        return {"error": "Not logged in"}

    cafe_id = request.args.get('cafe_id')
    cafe = Cafe.query.get_or_404(cafe_id)

    status = cafe in g.user.liked_cafes
    return jsonify(likes=status)


@app.post('/api/like')
def like_cafe():
    """
    Given JSON like {"cafe_id": 1}, make the current user like cafe
    with corresponding ID. Return JSON {"liked": 1}.
    """

    if not g.user:
        return {"error": "Not logged in"}

    cafe_id = request.json["cafe_id"]
    cafe = Cafe.query.get_or_404(cafe_id)

    g.user.liked_cafes.append(cafe)

    db.session.commit()

    return jsonify(liked=cafe_id)

@app.post('/api/unlike')
def unlike_cafe():
    """
    Given JSON like {"cafe_id": 1}, make the current user unlike cafe
    with corresponding ID. Return JSON like {"unliked": 1}.
    """

    if not g.user:
        return jsonify({"error": "Not logged in"})

    cafe_id = request.json["cafe_id"]
    like = Like.query.get_or_404((g.user.id, cafe_id))

    db.session.delete(like)
    db.session.commit()

    return jsonify(unliked=cafe_id)

#####################
# errors

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")
