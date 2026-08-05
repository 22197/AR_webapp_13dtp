"""Anonymous Report School - routes & code, Riki Smillie, 19/03/2026"""

# imports
# Flask
# SQL
import sqlite3

# Datetime
from datetime import datetime

# Flask
from flask import Flask, flash, render_template, request
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
from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from wtforms import (
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

app.config["SECRET_KEY"] = "really super secret key!"  # make sure to remove

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#login 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Create the database tables
with app.app_context():
    db.create_all()

# ______________________________________________________________________
# Create db model
# bridging table Report_Type (define before Reports class)
Report_Type = db.Table(
    "Report_Type",
    db.Column(
        "report_id", db.Integer, db.ForeignKey("Reports.report_id"), primary_key=True
    ),
    db.Column("type_id", db.Integer, db.ForeignKey("Type.type_id"), primary_key=True),
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
    report_id = db.Column(
        db.Integer, db.ForeignKey("Reports.report_id"), nullable=False
    )
    report = db.relationship("Reports", backref="notes")

#user table
class User(db.Model):
    __tablename__ = "User"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False )


# FORMS
# Check Boxes
class MultiCheckboxField(SelectMultipleField):
    # render the field as a list of checkboxes
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
    title = StringField("title")
    status = SelectField("status", choices=[])
    type = MultiCheckboxField("type", choices=[])
    priority = SelectField("priority", choices=[])
    note = TextAreaField("note", validators=[])
    update = SubmitField("Update")


# Login form
class LoginForm(FlaskForm):
    user_name = StringField("user_name")
    password = StringField("password")   
    # Submit
    submit = SubmitField("Submit") 

# sign up form
class SignupForm(FlaskForm):
    user_name = StringField("user_name")
    password = StringField("password")  
    # Submit
    submit = SubmitField("Submit")

    def validate_username(self, user_name):
        existing_user_name = User.query.filter_by(
            user_name=user_name.data).first()
        if existing_user_name:
            raise ValidationError(
                "This username already exists. Please choose another one."
            )
            
    

# ______________________________________________________________________
# routes


# route report.html
@app.route("/", methods=["GET", "POST"])
def report():
    title = None
    report = None
    form = ReportForm()
    # Check boxes
    form.type.choices = [(str(rt.type_id), rt.type) for rt in Type.query.all()]
    # validate form
    if form.validate_on_submit():
        title = form.title.data  # if form is filled, assign name
        form.title.data = ""  # reset for the next times

        report = form.report.data
        form.report.data = ""

        report_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        status_id = 3

        priority_id = 6

        new_report = Reports(
            report_title=title,
            report_detail=report,
            report_time=report_time,
            status_id=status_id,
            priority_id=priority_id
        )

        #####
        types = form.type.data
        # Loop through each selected type ID string
        for type_id_str in types:
            # Convert string ID to int and fetch Type object from db
            type_obj = Type.query.get(int(type_id_str))
            # Check if the Type object was found
            if type_obj:
                # Add the Type object to the report's many-to-many relationship
                new_report.types.append(type_obj)

        form.type.data = ""

        db.session.add(new_report)
        db.session.commit()
        return render_template("report.html", title=title, form=form)
    else:
        return render_template("report.html", form=form)
    # write render error messages


@app.route("/view", methods=["GET"])
def view():
    sort = request.args.get("sort", "original")
    if sort == "status":
        reports = Reports.query.join(Status).order_by(Status.status.asc()).all()
    elif sort == "type":
        reports = Reports.query.join(Reports.types).order_by(Type.type.asc()).all()
    elif sort == "priority":
        reports = Reports.query.join(Priority).order_by(Priority.priority.asc()).all()
    else:
        reports = Reports.query.order_by(Reports.report_id.asc()).all()
        
    status = Status.query.all()
    types = Type.query.all()
    priority = Priority.query.all()
    return render_template(
        "view.html", reports=reports, status=status, types=types, sort=sort, priority=priority
    )


@app.route("/edit/<int:report_id>", methods=["GET", "POST"])
def edit(report_id):
    form = EditForm()
    report_to_update = Reports.query.get_or_404(report_id)
    form.type.choices = [(str(rt.type_id), rt.type) for rt in Type.query.all()]
    form.status.choices = [(str(s.status_id), s.status) for s in Status.query.all()]
    form.priority.choices = [(str(p.priority_id), p.priority) for p in Priority.query.all()]

    if request.method == "GET":
        form.title.data = report_to_update.report_title

        form.note.data = ""

        form.status.data = str(report_to_update.status_id)

        form.priority.data = str(report_to_update.priority_id)

        form.type.data = [str(t.type_id) for t in report_to_update.types]

    if form.validate_on_submit():
        report_to_update.report_title = form.title.data
        report_to_update.status_id = int(form.status.data)
        report_to_update.priority_id = int(form.priority.data)
        selected_type_ids = [int(type_id) for type_id in form.type.data]
        report_to_update.types = [
            Type.query.get(type_id)
            for type_id in selected_type_ids
            if Type.query.get(type_id)
        ]

        if form.note.data:
            note_text = form.note.data
        else:
            note_text = ""

        if note_text:
            new_note = Notes(note=note_text, report_id=report_to_update.report_id)
            db.session.add(new_note)

        try:
            db.session.add(report_to_update)
            db.session.commit()
            flash("The Report Was Successfully updated!")
            form.note.data = ""
            report_to_update = Reports.query.get_or_404(report_id)
            return render_template(
                "edit_report.html", form=form, report_to_update=report_to_update
            )
        # return redirect(url_for('edit', report_id=report_id))
        except Exception:
            db.session.rollback()
            flash("Something Went Wrong!... please try again")
            return render_template(
                "edit_report.html", form=form, report_to_update=report_to_update
            )
    return render_template(
        "edit_report.html", form=form, report_to_update=report_to_update
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(user_name=form.user_name.data, password=hash_password)
        db.session.add(new_user)
        db.session.commit()
    return render_template("sign_up.html", form=form, )


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return render_template("view.html")
    return render_template("sign_up.html", form=form, )

@app.route("/logout", methods=["GET", "POST"])


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# _______________________________________________________________________


if __name__ == "__main__":
    app.run(debug=True)
