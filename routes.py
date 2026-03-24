'''Anonymous Report School - routes & code'''
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


