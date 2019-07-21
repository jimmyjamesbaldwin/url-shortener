from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired

class SubmitUrlForm(Form):
    url = StringField('', validators=[DataRequired()])