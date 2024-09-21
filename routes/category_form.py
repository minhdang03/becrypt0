from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CategoryForm(FlaskForm):
    name = StringField('Tên danh mục', validators=[DataRequired()])
    submit = SubmitField('Thêm danh mục')