"""Anonymous Report School - routes & code, Riki Smillie, 19/03/2026"""
# imports

import os

# Datetime
from datetime import datetime

from dotenv import load_dotenv

# Flask
from flask import Flask, flash, redirect, render_template, request, url_for

# hash
from flask_bcrypt import Bcrypt

# Flask Login
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

# SQL alchemy
from flask_sqlalchemy import SQLAlchemy

# FlaskForms
from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
    widgets,
)
from wtforms.validators import DataRequired, Length, ValidationError

app = Flask(__name__)


# initialise DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# make secret key
load_dotenv()
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") 

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#login 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ______________________________________________________________________
# Create db model
# bridging table Report_Type (define before Reports class)
Report_Type = db.Table(
    "Report_Type",
    db.Column(
        "report_id", db.Integer, db.ForeignKey("Reports.report_id"), primary_key=True
    ),
    db.Column(
        "type_id", db.Integer, db.ForeignKey("Type.type_id"), primary_key=True
        ),
)


# reports table
class Reports(db.Model):
    __tablename__ = "Reports"
    report_id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String, nullable=False)
    report_detail = db.Column(db.String, nullable=False)
    report_time = db.Column(db.String, nullable=False)
    # status relationship
    status_id = db.Column(db.Integer, db.ForeignKey("Status.status_id"), nullable=True)
    status = db.relationship("Status", backref="reports")
    # priority relationship
    priority_id = db.Column(db.Integer, db.ForeignKey("Priority.priority_id"), nullable=True)
    priority = db.relationship("Priority", backref="reports")
    # types relationship
    types = db.relationship("Type", secondary=Report_Type, backref="reports")


# status table (keep if needed elsewhere)
class Status(db.Model):
    __tablename__ = "Status"
    status_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)

# priority table
class Priority(db.Model):
    __tablename__ = "Priority"
    priority_id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String, nullable=False)


# type table
class Type(db.Model):
    __tablename__ = "Type"
    type_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)


# note table
class Notes(db.Model):
    __tablename__ = "Notes"
    note_id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String, nullable=False)
    # report relationship
    report_id = db.Column(
        db.Integer, db.ForeignKey("Reports.report_id"), nullable=False
    )
    report = db.relationship("Reports", backref="notes")
    # user relationship
    user_id = db.Column(
        db.Integer, db.ForeignKey("User.user_id"), nullable=False
    )
    user = db.relationship("User", backref="notes")

#user tabler
class User(UserMixin, db.Model):
    __tablename__ = "User"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False )
    teacher_code = db.Column(db.String, nullable=False, unique=True)

    # use database user_id as login id
    def get_id(self):
        return str(self.user_id)

# Create the database tables if not existing
with app.app_context():
    db.create_all()



# FORMS
# Check Boxes for types
class MultiCheckboxField(SelectMultipleField):
    '''make a list of checkboxes '''
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# Report Form
class ReportForm(FlaskForm):
    # Title
    title = StringField(
        "title",
        validators=[
            DataRequired(message="A title is required"),
            Length(
                min=5, max=50, message="The title must be between 5 and 50 characters"
            ),
        ],
    )
    # Report
    report = TextAreaField(
        "reports",
        validators=[
            DataRequired(message="An explanation is required"),
            Length(min=21, message="A more detailed explanation is required"),
            Length(max=4000, message="Please write a more consise explanation"),
        ],
    )
    # Check Boxes
    type = MultiCheckboxField(
        "type",
        choices=[],
        validators=[
            DataRequired(message="Please select a category"),
        ],
    )
    # Submit
    submit = SubmitField("Submit")


# Edit form
class EditForm(FlaskForm):
    title = StringField("title", validators=[
        DataRequired(message="A title is required"),
        Length(
            min=5, max=50, message="The title must be between 5 and 50 characters"
            ),
    ])
    status = SelectField("status", choices=[])
    type = MultiCheckboxField("type", choices=[])
    priority = SelectField("priority", choices=[])
    note = TextAreaField("note", validators=[
        Length(max=500, message="Your note is too long.")
    ])
    update = SubmitField("Update")


# Login form
class LoginForm(FlaskForm):
    user_name = StringField(
        "user_name",
        validators=[
            DataRequired(message="You forgot to enter your username!"),
            Length(max=20, message="Your username is too long."),
        ],
        )
    password = PasswordField(
        "password",
        validators=[
            DataRequired(message="You forgot to enter your password!"),
            Length(max=20, message="Your password is too long."),
        ],
        )   
    # Submit
    submit = SubmitField("Log In")  


# sign up form
class SignupForm(FlaskForm):
    user_name = StringField(
        "user_name",
        validators=[
            DataRequired(message="You must enter a username."),
            Length(max=20, message="The username must be below 20 characters."),
        ],
    )
    password = PasswordField(
        "password",
        validators=[
            DataRequired(message="You must enter a password."),
            Length(
                min=8,
                message="Please use a stronger password that is at least 8 characters.",
            ),
            Length(
                max=30,
                message="The password must be below 30 characters."),
        ],
    )
    teacher_code = StringField(
        "teacher_code",
        validators=[
            DataRequired(message="You must enter a teacher code."),
            Length(min=3, max=3, message="The teacher code must be exactly 3 characters long."),
        ],
    )
    submit = SubmitField("Sign Up")

    # make validator
    def validate_user_name(self, user_name):
        '''Check if the username already exists in the database'''
        existing_user_name = User.query.filter_by(
            user_name=user_name.data).first() # query for entered username
        if existing_user_name: # if the username exists in db
            raise ValidationError(
                "This username already exists. Please choose another one."
            )
        
    def validate_teacher_code(self, teacher_code):
        '''Check if the username already exists in the database'''
        existing_code = User.query.filter_by(
            teacher_code=teacher_code.data).first() # query for entered teacher code
        if existing_code: # if the teacehr code exists in db
            raise ValidationError(
                "This Teacher Code already exists. Please choose another one."
            )
            
    

# ______________________________________________________________________
# routes


# route report.html
@app.route("/", methods=["GET", "POST"])
def report():
    '''route for the report page - able to write in form to submit to database'''
    # Define form
    form = ReportForm()

    # Check boxes
    form.type.choices = [(str(rt.type_id), rt.type) for rt in Type.query.all()] # query all type from type tabel

    # validate form
    if form.validate_on_submit():
        title = form.title.data  # if form is filled, assign name
        report = form.report.data

        #report time when form was submit
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M") # make report_time show only date, hour and minutes

        # set status id to 3 so initially "NOT checked"
        status_id = 3

        # set priority id to 6 so initially "Not set"
        priority_id = 6

        new_report = Reports(
            report_title=title,
            report_detail=report,
            report_time=report_time,
            status_id=status_id,
            priority_id=priority_id
        )

        # selected types are added to new_report
        types = form.type.data
        for type_id_str in types: # loop each type
            type_obj = Type.query.get(int(type_id_str)) # query for type with the type id
            if type_obj:
                new_report.types.append(type_obj) # add to new report

        try:
            db.session.add(new_report) # add to db session
            db.session.commit() # commit to db

            form.title.data = ""  # reset for the next time 
            form.report.data = ""
            form.type.data = []

            return render_template("report.html", title=title, form=form) #also return title to say report was submit
        except Exception:
            db.session.rollback() # take db session back
            flash("Something Went Wrong! Please try again...") # tell user it didn't work
            return render_template("report.html", form=form)
    else:
        return render_template("report.html", form=form)

@app.route("/view", methods=["GET"])
@login_required # only be accessed if the user is logged in
def view():
    '''route for viewing all the reports - links to specific pages for each report '''
    sort = request.args.get("sort", "original") # check how the user wants to sort
    # query for reports based on how the user wants to sort
    if sort == "status":
        reports = Reports.query.join(Status).order_by(Status.status.asc()).all()
    elif sort == "type":
        reports = Reports.query.join(Reports.types).order_by(Type.type.asc()).all()
    elif sort == "priority":
        reports = Reports.query.join(Priority).order_by(Priority.priority.asc()).all()
    else:
        reports = Reports.query.order_by(Reports.report_id.asc()).all()

    # query for the content in status types and priority
    status = Status.query.all()
    types = Type.query.all()
    priority = Priority.query.all()
    return render_template(
        "view.html", reports=reports, status=status, types=types, sort=sort, priority=priority
    )


@app.route("/edit/<int:report_id>", methods=["GET", "POST"])
@login_required # only be accessed if the user is logged in
def edit(report_id):
    '''edit page to fix, edit reports'''
    # define form
    form = EditForm()

    # query for the report (404 if the report doesn't exist)
    report_to_update = Reports.query.get_or_404(report_id)
    # query everything from type, status and priority (id and name)
    form.type.choices = [(str(rt.type_id), rt.type) for rt in Type.query.all()]
    form.status.choices = [(str(s.status_id), s.status) for s in Status.query.all()]
    form.priority.choices = [(str(p.priority_id), p.priority) for p in Priority.query.all()]

    # when page is opened, fill form with what already exists
    if request.method == "GET":
        form.title.data = report_to_update.report_title

        form.note.data = "" # note is blank, want a new form to be written each time.

        form.status.data = str(report_to_update.status_id)

        form.priority.data = str(report_to_update.priority_id)

        form.type.data = [str(t.type_id) for t in report_to_update.types]

    # add form content to report_to_update
    if form.validate_on_submit():
        # report details can't be updated
        report_to_update.report_title = form.title.data
        report_to_update.status_id = int(form.status.data)
        report_to_update.priority_id = int(form.priority.data)
        #type
        selected_type_ids = [int(type_id) for type_id in form.type.data] # make list of type id selected

        report_to_update.type = []
        for type_id in selected_type_ids: 
            rt = Type.query.get(type_id)
            if rt:
                report_to_update.type.append(rt) # add type to report_to_update

        # if a note was written, add to db session
        if form.note.data:
            new_note = Notes(
                note=form.note.data, 
                report_id=report_to_update.report_id,
                user_id=current_user.user_id
                )
            db.session.add(new_note)

        # try commit to db 
        try:
            db.session.add(report_to_update)
            db.session.commit()
            # commit to db
            flash("The Report Was Successfully updated!") # tell user that it was submitted
            form.note.data = "" # clear note field for next time
            return render_template(
                "edit_report.html", form=form, report_to_update=report_to_update
            )
        # if commit to db doesn't work, 
        except Exception:
            db.session.rollback() # take db session back
            flash("Something Went Wrong! Please try again...") # tell user it didn't work
            return render_template(
                "edit_report.html", form=form, report_to_update=report_to_update
            )
    return render_template(
        "edit_report.html",
        form=form,
        report_to_update=report_to_update,
    )


@app.route("/signup", methods=["GET", "POST"])
@login_required # only be accessed if the user is logged in
def signup():
    '''Sign up page for users to make accounts'''
    form = SignupForm() # define form
    if form.validate_on_submit():

        hash_password = bcrypt.generate_password_hash(form.password.data) # hash password

        new_user = User(user_name=form.user_name.data,
                        teacher_code=form.teacher_code.data,
                        password=hash_password)
        
        db.session.add(new_user)
        db.session.commit() # commit to db
        return redirect(url_for("login")) # take user to login page so they can login with new account
    return render_template("sign_up.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    '''Login page for user'''
    form = LoginForm() # define from

    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first() # query for usename

        if user and bcrypt.check_password_hash(user.password, form.password.data): # check if username and hashed password match
            login_user(user) # login
            return redirect(url_for("view")) # take to view page
        flash("Your username or password is wrong!!", "danger") # tell user that they made a mistake
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    '''logout the user'''
    logout_user()
    return redirect(url_for("report"))


@app.route("/about")
def about():
    '''take to logout page'''
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    '''404 error'''
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
