from flask.ext.wtf import Form
from wtforms import StringField, SelectField, DateField
from wtforms.validators import DataRequired, Length

class DescendantsSearchByTagForm(Form):
  tag = SelectField('tag')
  layer = ""

class DescendantsSearchByIdForm(Form):
  rawid = StringField('rawid')

