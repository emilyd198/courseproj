import os
from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from sqlalchemy import text, column, engine, or_
from wtforms import StringField, SubmitField, IntegerField, SelectField, EmailField, URLField
from wtforms.validators import DataRequired, NumberRange, URL, Email, Length, ValidationError, AnyOf
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/course_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)

db = SQLAlchemy(app)


class Sections(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    number_id = db.Column(db.Integer, db.ForeignKey('numbers.id'))
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'))
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))

    courses = db.relationship('Courses', back_populates='sections')
    numbers = db.relationship('Numbers', back_populates='course')
    professors = db.relationship('Professors', back_populates='teaching')
    meetings = db.relationship('Meetings', back_populates='classes')

    def __repr__(self):
        return '<Section %r>' % self.courses


class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(64))
    title = db.Column(db.String(64))
    department_id = db.Column(db.Integer(), db.ForeignKey('departments.id'))

    sections = db.relationship('Sections', back_populates='courses')

    def __repr__(self):
        return 'Course %r' % self.course


class Departments(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    course = db.relationship('Courses', backref='department')

    def __repr__(self):
        return '%r' % self.code


class Numbers(db.Model):
    __tablename__ = 'numbers'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)

    course = db.relationship('Sections', back_populates='numbers')

    def __repr__(self):
        return '<Number %r>' % self.number


class Professors(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(64))

    teaching = db.relationship('Sections', back_populates='professors')

    def __repr__(self):
        return '<Professor %r>' % self.full_name


class Meetings(db.Model):
    __tablename__ = 'meetings'
    id = db.Column(db.Integer, primary_key=True)
    days = db.Column(db.String(64))
    start = db.Column(db.Time)
    end = db.Column(db.Time)

    classes = db.relationship('Sections', back_populates='meetings')

    def __repr__(self):
        return '<Meeting %r>' % self.start


class DeptForm(FlaskForm):
    """
    Class that defines an information form. Fields are defined a class variables. Class variables are assigned
    to objects with field types and validators.
    """
    department1 = SelectField('Department 1', choices=['ACP', 'AMS', 'ANT', 'ART', 'BCM', 'BIO', 'BUS', 'CHM', 'CHN',
                                                       'COM', 'CSC', 'DAN', 'DAT', 'ECN', 'EDC', 'EGR', 'EHS', 'ENG',
                                                       'ENV', 'FRN', 'FYS', 'GEO', 'GRM', 'HCA', 'HNR', 'HST', 'HUM',
                                                       'IPH', 'ISC', 'LIB', 'MTH', 'MUS', 'NMS', 'NUR', 'OSP', 'PHL',
                                                       'PHY', 'POL', 'PSY', 'REL', 'SOC', 'SPN', 'THE', 'WGS'],
                              validators=[DataRequired()])

    department2 = SelectField('Department 2', choices=['ACP', 'AMS', 'ANT', 'ART', 'BCM', 'BIO', 'BUS', 'CHM', 'CHN',
                                                       'COM', 'CSC', 'DAN', 'DAT', 'ECN', 'EDC', 'EGR', 'EHS', 'ENG',
                                                       'ENV', 'FRN', 'FYS', 'GEO', 'GRM', 'HCA', 'HNR', 'HST', 'HUM',
                                                       'IPH', 'ISC', 'LIB', 'MTH', 'MUS', 'NMS', 'NUR', 'OSP', 'PHL',
                                                       'PHY', 'POL', 'PSY', 'REL', 'SOC', 'SPN', 'THE', 'WGS'],
                              validators=[DataRequired()])
    def validate_department2(self, field):
        """
        function to validate email ends with @alma.edu domain
        :param field:
        :raises: ValidationError
        """
        if self.department1.data == self.department2.data:
            raise ValidationError('Departments can not be the same, please choose a different department')

    submit = SubmitField('Submit')

class AddForm(FlaskForm):
    course = StringField('Course Code', validators=[DataRequired()])
    title = StringField('Course Title', validators=[DataRequired()])
    # department = SelectField('Department', choices=[results])
    department = SelectField('Department', choices=['ART', 'AMS', 'ANT', 'ART', 'BCM', 'BIO', 'BUS', 'CHM', 'CHN',
                                                       'COM', 'CSC', 'DAN', 'DAT', 'ECN', 'EDC', 'EGR', 'EHS', 'ENG',
                                                       'ENV', 'FRN', 'FYS', 'GEO', 'GRM', 'HCA', 'HNR', 'HST', 'HUM',
                                                       'IPH', 'ISC', 'LIB', 'MTH', 'MUS', 'NMS', 'NUR', 'OSP', 'PHL',
                                                       'PHY', 'POL', 'PSY', 'REL', 'SOC', 'SPN', 'THE', 'WGS'])

    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    """
    error handler if server cannot find the requested resource.
    :param e: event
    :return: 404.html template
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    error handler if server encountered an unexpected
    condition that prevented it from fulfilling the request.
    :param e: event
    :return: 500.html template
    """
    return render_template('500.html'), 500


@app.route('/')
def index():
    """
    function that defines a route in Flask and display the form.
    :return: index.html template
    """
    form = DeptForm()
    session['course_info'] = {} # List course info
    return render_template('index.html', form=form, department1=session.get('department1'),
                           department2=session.get('department2'))


@app.route('/', methods=['GET', 'POST'])
def submit():
    """
    function that defines a route in Flask and display the form and updates after form is submitted.
    :return: response.html template
    """
    form = DeptForm()
    if form.validate_on_submit():
        session['department1'] = form.department1.data
        session['department2'] = form.department2.data
        choice1 = db.session.query(Departments).filter(Departments.code == form.department1.data).all()
        choice2 = db.session.query(Departments).filter(Departments.code == form.department2.data).all()

        for row in choice1:
            get_id1 = row.id
        for row in choice2:
            get_id2 = row.id
        query = db.session.query(Courses).filter(or_(Departments.id == get_id1, Departments.id == get_id2)).\
            join(Departments, Courses.department_id == Departments.id).join(Sections,Courses.id == Sections.course_id).\
            join(Numbers, Sections.number_id == Numbers.id).join(Professors, Sections.professor_id == Professors.id).\
            join(Meetings, Sections.meeting_id == Meetings.id).all()

        for row in query:
            session['course_info'].update({row.course: row.title})
        # for row in query:
        #     print(row.course, row.title, row.full_name)

        for key, value in session['course_info'].items():
            print(key, ' : ', value)
        # results = db.session.query(Departments, Courses).filter(Departments.id == Courses.department_id).all()
        # results = db.session.query(Sections, Departments, Courses).filter(Departments.id == Sections.courses).all()

        return render_template('response.html', form=form, department1=session.get('department1'),
                               department2=session.get('department2'), choice1=choice1, choice2=choice2,key=key,
                               value=value, course_info=session.get('course_info'))


@app.route('/add', methods=['GET', 'POST'])
def add_course():

    form = AddForm()
    if form.validate_on_submit():
        session['course'] = form.course.data
        session['title'] = form.title.data
        session['department'] = form.department.data
        results = db.session.query(Departments).filter(Departments.code == form.department.data).all()
        print(results)
        course_add = Courses.query.filter_by(title=form.title.data).first()
        if course_add is None:
            course_add = Courses(course=form.course.data, title=form.title.data)
            # course_add = Courses(course=form.course.data, title=form.title.data, department=results)
            db.session.add(course_add)
            db.session.commit()
        flash("Course Added Successfully")
    # name_to_update = Courses.query.get_or_404(id)
    # if request.method == 'POST':
    #     name_to_update.course = request.from['name']

    return render_template('add_course.html', form=form, courseadd=session.get('course'),
                           titleadd=session.get('title'), deptadd=session.get('department'))


if __name__ == '__main__':
    app.run()

