import os
from flask import Flask, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf import FlaskForm
from sqlalchemy import or_
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/course_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Sections(db.Model):
    """Class that defines the sections model."""
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
    """Class that defines the courses model."""
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(64))
    title = db.Column(db.String(64))
    department_id = db.Column(db.Integer(), db.ForeignKey('departments.id'))

    sections = db.relationship('Sections', back_populates='courses')

    def __repr__(self):
        return 'Course %r' % self.course


class Departments(db.Model):
    """Class that defines the departments model."""
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    course = db.relationship('Courses', backref='department')

    def __repr__(self):
        return '%r' % self.code


class Numbers(db.Model):
    """Class that defines the numbers model."""
    __tablename__ = 'numbers'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)

    course = db.relationship('Sections', back_populates='numbers')

    def __repr__(self):
        return '<Number %r>' % self.number


class Professors(db.Model):
    """Class that defines the professors model."""
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(64))

    teaching = db.relationship('Sections', back_populates='professors')

    def __repr__(self):
        return '<Professor %r>' % self.full_name


class Meetings(db.Model):
    """Class that defines the meetings model."""
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
    Class that defines an information form to choose two departments. Fields are defined a class variables.
    Class variables are assigned to objects with field types and validators.
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
        function to validate that department choices are not the same
        :param field:
        :raises: ValidationError
        """
        if self.department1.data == self.department2.data:
            raise ValidationError('Departments can not be the same, please choose a different department')

    submit = SubmitField('Submit')


class AddForm(FlaskForm):
    """
    Class that defines an information form to add a new course. Fields are defined a class variables.
    Class variables are assigned to objects with field types and validators.
    """
    course = StringField('Course Code', validators=[DataRequired()])
    title = StringField('Course Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    """
    function that defines a route in Flask and displays the form.
    :return: index.html template
    """
    form = DeptForm()
    return render_template('index.html', form=form, department1=session.get('department1'),
                           department2=session.get('department2'))


@app.route('/', methods=['GET', 'POST'])
def submit():
    """
    function that defines a route in Flask and displays the form to compare two department's courses and load them
     into a table after form is submitted.
    :return: response.html template
    """
    form = DeptForm()
    session['course_info'] = {}  # dictionary of course info
    session['values'] = []  # list of values for dictionary
    if form.validate_on_submit():
        session['department1'] = form.department1.data
        session['department2'] = form.department2.data
        choice1 = db.session.query(Departments).filter(Departments.code == form.department1.data).all()
        choice2 = db.session.query(Departments).filter(Departments.code == form.department2.data).all()

        for row in choice1:
            get_id1 = row.id
        for row in choice2:
            get_id2 = row.id
        query = db.session.query(Departments.code, Departments.name, Courses.course, Numbers.number, Courses.title,
                                 Professors.full_name, Meetings.days, Meetings.start, Meetings.end).filter(or_(
            Departments.id == get_id1, Departments.id == get_id2)). \
            join(Departments, Courses.department_id == Departments.id).join(Sections, Courses.id == Sections.course_id). \
            join(Numbers, Sections.number_id == Numbers.id).join(Professors, Sections.professor_id == Professors.id). \
            join(Meetings, Sections.meeting_id == Meetings.id)

        print(query)
        for row in query:
            session['values'].append(row.course)
            session['values'].append(row.code)
            session['values'].append(row.number)
            session['values'].append(row.name)
            session['values'].append(row.full_name)
            session['values'].append(row.days)
            session['values'].append(str(row.start))
            session['values'].append(str(row.end))
            session['course_info'].update({row.title: session['values']})
            session['values'] = []
    return render_template('response.html', form=form, department1=session.get('department1'),
                           department2=session.get('department2'),
                           course_info=session.get('course_info'))


@app.route('/add', methods=['GET', 'POST'])
def add_course():
    """
    function that defines a route in Flask and display a form to add a course to the database.
    :return: add_course.html template
    """
    form = AddForm()
    session['course'] = form.course.data
    session['title'] = form.title.data
    if form.validate_on_submit():
        course_add = Courses.query.filter_by(title=form.title.data).first()
        if course_add is None:
            course_add = Courses(course=form.course.data, title=form.title.data)
            db.session.add(course_add)
            db.session.commit()
            flash("Course Added Successfully")
        else:
            flash("Course already exists, please add a different course")

    return render_template('add_course.html', form=form, courseadd=session.get('course'),
                           titleadd=session.get('title'))


if __name__ == '__main__':
    app.run()
