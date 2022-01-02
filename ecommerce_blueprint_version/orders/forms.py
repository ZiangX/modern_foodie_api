from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class importExcelForm(FlaskForm):
    excel_file = FileField('Excel file', validators=[
        FileAllowed(['xlsx']), DataRequired()])
    confirm = BooleanField('Please check the data first before checking the box')
    submit = SubmitField('Save')
