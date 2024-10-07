from flask import Flask, render_template, url_for, redirect, request, flash, session,send_from_directory
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField , SubmitField
from wtforms.validators import InputRequired, Length, DataRequired
from flask_bcrypt import Bcrypt

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('INICIO-SESION/index.html')

@app.route('/static/')
def serve_static(path):
    return send_from_directory(
        app.config['static'],path, as_attachment=True
  )

if __name__ == '__main__':
    app.run()