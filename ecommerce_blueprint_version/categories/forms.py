from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class addCategoryForm(FlaskForm):
    category_name_zh = StringField(
        'Category Name in Chinese', validators=[DataRequired()])
    category_name_en = StringField(
        'Category Name in English', validators=[DataRequired()])
    category_name_fr = StringField(
        'Category Name in French', validators=[DataRequired()])
    category_img = FileField('Category Image', validators=[
        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save')
