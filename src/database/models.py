import os
from flask_sqlalchemy.model import Model
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

project_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get('DATABASE_URL')

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)


'''
Issue
a persistant issue entity, extends the base SQLAlchemy Model
'''


class Issue(db.Model):
    __tablename__ = 'issues'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), unique=True, nullable=False)
    open = Column(Boolean, default=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    last_modified = Column(DateTime, nullable=True)

    # Foreign key
    user_id = Column(String, ForeignKey('users.id'), nullable=False)

    # Relationships
    comments = db.relationship('Comment', backref='issue')

    def __repr__(self):
        return f'<Issue #{self.id}: #{self.title}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    format_no_comments()
        short form representation of the Issue model
        without related comments
    '''

    def format_no_comments(self):
        return {
            'id': self.id,
            'title': self.title,
            'open': self.open,
            'text': self.text,
            'created_at': self.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
            'closed_at': self.closed_at.strftime("%m/%d/%Y, %H:%M:%S"),
            'last_modified': self.last_modified.strftime("%m/%d/%Y, %H:%M:%S"),
            'user': self.user.format_short
        }

    '''
    format_with_comments()
        long form representation of the Issue model
        with related comments
    '''

    def format_with_comments(self):
        return {
            'id': self.id,
            'title': self.title,
            'open': self.open,
            'text': self.text,
            'created_at': self.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
            'closed_at': self.closed_at.strftime("%m/%d/%Y, %H:%M:%S"),
            'last_modified': self.last_modified.strftime("%m/%d/%Y, %H:%M:%S"),
            'user': self.user.format_short,
            'comments': self.comments.format
        }


'''
User
a persistant user entity, extends the base SQLAlchemy Model
'''


class User(db.Model):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(320), nullable=False)
    date_joined = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=False)
    role = Column(String(100))

    # relationships
    issues = db.relationship('Issue', backref='user')
    comments = db.relationship('Comment', backref='user')

    def __repr__(self):
        return f'<User #{self.username}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    format_short()
        short form representation of the User model
    '''

    def format_short(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'role': self.role
        }

    '''
    TODO other formats: wait for implementation
    '''


'''
Comment
a persistant comment entity, extends the base SQLAlchemy Model
'''


class Comment(db.Model):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_modified = Column(DateTime, nullable=False)

    # Foreign keys
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    issue_id = Column(Integer, ForeignKey('issues.id'), nullable=False)

    def __repr__(self):
        return f'<Comment #{self.id} by #{self.user} on issue #{self.issue_id}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    format()
        representation of the Comment model
    '''

    def format(self):
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
            'last_modified': self.last_modified.strftime("%m/%d/%Y, %H:%M:%S"),
            'user': self.user,
            'issue': self.issue
        }
