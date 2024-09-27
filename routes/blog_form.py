from models.categories import Category
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, HiddenField, SubmitField, SelectField
from wtforms.validators import DataRequired

class BlogForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired()])
    category_id = SelectField('Danh mục', choices=[], coerce=int, validators=[DataRequired()])
    content = TextAreaField('Nội dung', validators=[DataRequired()])
    thumbnail_url = StringField('Ảnh Cover')
    user_id = HiddenField('User ID')
    submit = SubmitField('Đăng bài')

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]