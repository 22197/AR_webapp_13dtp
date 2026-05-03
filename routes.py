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
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
# Datetime
from datetime import datetime


app = Flask(__name__)


# initialise DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = "really super secret key!"  # make sure to remove


# Create db model
# reports table
class Reports(db.Model):
    __tablename__ = "Reports"
    report_id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String(20), nullable=False)
    report_detail = db.Column(db.String(1000), nullable=False)
    report_time = db.Column(db.String, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('Status.status_id'))

# status table
class Status(db.Model):
    __tablename__ = "Status"
    status_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False)


# create Form class
# Report
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
    # Checkboxes
        
    # Submit
    submit = SubmitField(
        "Submit"
        )
# Notes

# route report.html
@app.route('/', methods=['GET', 'POST'])
def report():
    title = None
    report = None
    form = ReportForm()
    # validate form
    if form.validate_on_submit():
        title = form.title.data  # if form is filled, asign name
        form.title.data = ''  # reset for the next times
        report = form.report.data
        form.report.data = ''
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        status = '3'

        new_report = Reports(report_title=title,
                             report_detail=report,
                             report_time=report_time,
                             status_id=status)
        db.session.add(new_report)
        db.session.commit()

    return render_template("report.html", title=title,
                           form=form,
                           report=report)


# ______________________________________________________________________


@app.route('/about')
def about():
    return render_template("about.html")


# _______________________________________________________________________


if __name__ == "__main__":
    app.run(debug=True)
