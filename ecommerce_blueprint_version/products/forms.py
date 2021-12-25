from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, FloatField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed

class addProductForm(FlaskForm):
    category = SelectField('Category:', coerce=int, id='select_category')
    product_name_zh = StringField(
        'Product Name in Chinese:', validators=[DataRequired()])
    product_name_en = StringField(
        'Product Name in English:', validators=[DataRequired()])
    product_name_fr = StringField(
        'Product Name in French:', validators=[DataRequired()])
    description_zh = TextAreaField(
        'Product Description in Chinese:', validators=[DataRequired()])
    description_en = TextAreaField(
        'Product Description in English:', validators=[DataRequired()])
    description_fr = TextAreaField(
        'Product Description in French:', validators=[DataRequired()])
    productPrice = FloatField('Product Price:', validators=[Optional()])
    productVariant1 = StringField('Product variant 1:', validators=[Optional()])
    productVariant2 = StringField('Product variant 2:', validators=[Optional()])
    productVariant3 = StringField('Product variant 3:', validators=[Optional()])
    productVariant4 = StringField('Product variant 4:', validators=[Optional()])
    productVariant5 = StringField('Product variant 5:', validators=[Optional()])
    productQuantity = IntegerField(
        'Product Quantity:', validators=[DataRequired()])
    product_imgs = MultipleFileField('Product Images', validators=[
        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save')
