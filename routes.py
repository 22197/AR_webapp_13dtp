'''Anonymous Report School - routes & code, Riki Smillie, 19/03/2026'''
# imports
# Flask
from flask import Flask, request, render_template
# SQL
import sqlite3
# Flask Login
import flask_login
# SQL alchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, select
# FlaskForms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import DataRequired
# Datetime
from datetime import datetime


app = Flask(__name__)


# initialise DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Create the database tables
with app.app_context():
    db.create_all()

app.config['SECRET_KEY'] = "really super secret key!"  # make sure to remove

# ______________________________________________________________________
# Create db model
# bridging table Report_Type (define before Reports class)
Report_Type = db.Table(
    'Report_Type',
    db.Column(
        'report_id',
        db.Integer,
        db.ForeignKey('Reports.report_id'),
        primary_key=True),
    db.Column(
        'type_id',
        db.Integer,
        db.ForeignKey('Type.type_id'),
        primary_key=True)
)


# reports table
class Reports(db.Model):
    __tablename__ = "Reports"
    report_id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String(20), nullable=False)
    report_detail = db.Column(db.String(1000), nullable=False)
    report_time = db.Column(db.String, nullable=False)
    # status relationship
    status_id = db.Column(db.Integer, db.ForeignKey('Status.status_id'),
                          nullable=True
                          )
    status = db.relationship('Status', backref='reports')
    # types relationship
    types = db.relationship('Type', secondary=Report_Type, backref='reports')


# status table (keep if needed elsewhere)
class Status(db.Model):
    __tablename__ = "Status"
    status_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)


# type table
class Type(db.Model):
    __tablename__ = "Type"
    type_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)


# create Form class
# Check Boxes
class MultiCheckboxField(SelectMultipleField):
    # render the field as a list of checkboxes
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# Report Form
class ReportForm(FlaskForm):
    # Title
    title = StringField(
        "Please write a title for this incident...",
        validators=[
            DataRequired()
            ])
    # Report
    report = TextAreaField(
        "Please report any incidents here...",
        validators=[
            DataRequired()
            ])
    # Check Boxes
    type = MultiCheckboxField('type', choices=[])
    # Submit
    submit = SubmitField(
        "Submit"
        )

# ______________________________________________________________________
# routes


# route report.html
@app.route('/', methods=['GET', 'POST'])
def report():
    title = None
    report = None
    form = ReportForm()
    # Check boxes
    form.type.choices = [
        (str(rt.type_id), rt.type)
        for rt in Type.query.all()
        ]
    # validate form
    if form.validate_on_submit():
        title = form.title.data  # if form is filled, assign name
        form.title.data = ''  # reset for the next times

        report = form.report.data
        form.report.data = ''

        report_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        new_report = Reports(
            report_title=title,
            report_detail=report,
            report_time=report_time
            )

        # help from COPILOT
        types = form.type.data
        # Loop through each selected type ID string
        for type_id_str in types:
            # Convert string ID to int and fetch Type object from db
            type_obj = Type.query.get(int(type_id_str))
            # Check if the Type object was found
            if type_obj:
                # Add the Type object to the report's many-to-many relationship
                new_report.types.append(type_obj)

        form.type.data = ''

        db.session.add(new_report)
        db.session.commit()

    return render_template("report.html", title=title,
                           form=form
                           )


@app.route('/view')
def view():
    reports = Reports.query.all()
    status = Status.query.all()
    types = Type.query.all()
    return render_template(
        "view.html",
        reports=reports,
        status=status,
        types=types,
    )


@app.route('/report/<int:report_id>')
def reports(report_id):
    reports = Reports.query.filter_by(report_id=report_id).scalar()
    status = Status.query.all()
    type = Type.query.all()
    return render_template(
        "edit_report.html",
        reports=reports,
        status=status,
        type=type
        )


@app.route('/about')
def about():
    return render_template("about.html")


'''@app.route('/404')
def _404():
    return render_template("404.html")'''

# _______________________________________________________________________


if __name__ == "__main__":
    app.run(debug=True)
