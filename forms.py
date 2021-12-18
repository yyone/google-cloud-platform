from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms.validators import DataRequired, Length

class MyForm(FlaskForm):
  message = StringField(
    "message",
    validators=[
      DataRequired(),
      Length(max=10),
    ],
  )
