import os
import json

from flask_sqlalchemy.model import Model
from sqlalchemy import ARRAY, Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get('DATABASE_URL')

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# setup_db(app)
#     binds a flask application and a SQLAlchemy service
#----------------------------------------------------------------------------#


def setup_db(app, database_path=DATABASE_URL):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


#----------------------------------------------------------------------------#
# Issue
# a persistant issue entity, extends the base SQLAlchemy Model
#----------------------------------------------------------------------------#

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
    user = db.relationship(
        'User',
        backref='issues',
        cascade='all, delete',
        foreign_keys=[user_id]
    )

    def __repr__(self):
        return f'<Issue #{self.id}: {self.title}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    #----------------------------------------------------------------------------#
    # format_no_comments()
    #     short form representation of the Issue model
    #     without related comments
    #----------------------------------------------------------------------------#

    def format_no_comments(self):
        created_at = self.created_at
        closed_at = self.closed_at
        last_modified = self.last_modified

        if created_at:
            created_at = created_at.strftime("%m/%d/%Y, %H:%M:%S")

        if closed_at:
            closed_at = closed_at.strftime("%m/%d/%Y, %H:%M:%S")

        if last_modified:
            last_modified = last_modified.strftime("%m/%d/%Y, %H:%M:%S")

        return {
            'id': self.id,
            'title': self.title,
            'open': self.open,
            'text': self.text,
            'created_at': created_at,
            'closed_at': closed_at,
            'last_modified': last_modified,
            'user': self.user.format_short()
        }

    #----------------------------------------------------------------------------#
    # format_with_comments()
    #     long form representation of the Issue model
    #     with related comments
    #----------------------------------------------------------------------------#

    def format_with_comments(self):
        created_at = self.created_at
        closed_at = self.closed_at
        last_modified = self.last_modified

        if created_at:
            created_at = created_at.strftime("%m/%d/%Y, %H:%M:%S")

        if closed_at:
            closed_at = closed_at.strftime("%m/%d/%Y, %H:%M:%S")

        if last_modified:
            last_modified = last_modified.strftime("%m/%d/%Y, %H:%M:%S")

        return {
            'id': self.id,
            'title': self.title,
            'open': self.open,
            'text': self.text,
            'created_at': created_at,
            'closed_at': closed_at,
            'last_modified': last_modified,
            'user': self.user.format_short(),
            'comments': {comment.id: comment.format() for comment in self.comments}
        }


#----------------------------------------------------------------------------#
# User
# a persistant user entity, extends the base SQLAlchemy Model
#----------------------------------------------------------------------------#


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    auth_id = Column(String, nullable=False)
    nickname = Column(String(100))
    name = Column(String(200))
    email = Column(String(320), nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=False)
    roles = Column(ARRAY(String(100)))

    def __repr__(self):
        return f'<User {self.nickname}>'

    # __getitem__ to iterate in PATCH /users endpoint
    # return None if key not found instead of raising KeyError
    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return None

    # __setitem__ to iterate in PATCH /users endpoint
    def __setitem__(self, key, value):
        if key in self.__dict__:
            setattr(self, key, value)
        else:
            raise KeyError(key)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    #----------------------------------------------------------------------------#
    # format_short()
    #     short form representation of the User model
    #----------------------------------------------------------------------------#

    def format_short(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'name': self.name,
            'roles': self.roles
        }

    '''
    TODO other formats: wait for implementation
    '''


#----------------------------------------------------------------------------#
# Comment
# a persistant comment entity, extends the base SQLAlchemy Model
#----------------------------------------------------------------------------#


class Comment(db.Model):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_modified = Column(DateTime, nullable=True)

    # Foreign keys
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    issue_id = Column(Integer, ForeignKey('issues.id'), nullable=False)

    # relationships
    user = db.relationship(
        'User',
        backref='comments',
        cascade='all, delete',
        foreign_keys=[user_id]
    )
    issue = db.relationship(
        'Issue',
        backref='comments',
        cascade='all, delete',
        foreign_keys=[issue_id]
    )

    def __repr__(self):
        return f'<Comment #{self.id} by {self.user} on issue {self.issue_id}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    #----------------------------------------------------------------------------#
    # format()
    #     representation of the Comment model
    #----------------------------------------------------------------------------#

    def format(self):
        created_at = self.created_at
        last_modified = self.last_modified

        if created_at:
            created_at = created_at.strftime("%m/%d/%Y, %H:%M:%S")

        if last_modified:
            last_modified = last_modified.strftime("%m/%d/%Y, %H:%M:%S")

        return {
            'id': self.id,
            'text': self.text,
            'created_at': created_at,
            'last_modified': last_modified,
            'user_id': self.user_id,
            'issue_id': self.issue_id
        }
