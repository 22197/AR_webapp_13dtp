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
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)


# initialise DB
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = "really super secret key!"  # make sure to remove


# create Form class
class NameForm(FlaskForm):
    title = StringField("Please write a title for this incident...", 
                            validators=[DataRequired()])
    report = StringField("Please report any incidents here...", 
                            validators=[DataRequired()])
    submit = SubmitField("Submit")


# routes
@app.route('/report', methods=['GET', 'POST'])
def report():
    title = None
    report = None
    form = NameForm()
    # validate form
    if form.validate_on_submit():
        title = form.title.data  # if form is filled, asign name
        form.title.data = ''  # reset for the next times
        report = form.report.data
        form.report.data = ''
    return render_template("report.html", title=title, report=report,
                           form=form)


if __name__ == "__main__":
    app.run(debug=True)