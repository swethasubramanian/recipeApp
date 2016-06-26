from flask.ext.wtf import Form

from wtforms.fields import TextField, FieldList, FormField
from wtforms.validators import DataRequired, Required

class inventory(Form):
    veggie = TextField('veggie', validators=[DataRequired()])
    quantity = TextField('quantity', validators=[DataRequired()])

class inventoryAll(Form):
	inventories = FieldList(FormField(inventory), min_entries=5, max_entries=10)
