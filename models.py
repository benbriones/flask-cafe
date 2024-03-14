"""Data models for Flask Cafe"""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()
DEFAULT_PROF_IMG_URL = '/static/images/default-pic.png'


class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )

    @classmethod
    def get_choices(self):
        """
        gets all current cities from database, returns list
        of tuples (city code, city name)
        """
        return [(city.code, city.name) for city in City.query.all()]



class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
        default = ""
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default="/static/images/default-cafe.png"
    )

    city = db.relationship("City", backref='cafes')

    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'


class User(db.Model):
    """Users in System"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False, # might change?
    )

    email = db.Column(
        db.Text,
        nullable=False
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default='/static/images/default-pic.png'
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


    def get_full_name(self):
        """returns user's full name"""

        return f"{self.first_name} {self.last_name}"

    @classmethod
    def register(cls,
                 username,
                 email,
                 first_name,
                 last_name,
                 password,
                 description='',
                 image_url=DEFAULT_PROF_IMG_URL,
                 admin=False
                 ):
        """Register user w/ a hashed password & return user"""

        hashed = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = cls(username=username,
                   admin=admin or False,
                   email=email,
                   first_name=first_name,
                   last_name=last_name,
                   description=description or '',
                   image_url=image_url or DEFAULT_PROF_IMG_URL,
                   password=hashed)
    #TODO: check these params, is the default img needed?
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user given a username & password
        returns user insance or False if not found/wrong password"""

        user = cls.query.filter_by(username=username).one_or_none()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False






def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
