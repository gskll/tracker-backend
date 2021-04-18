
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from api import create_app
from api.models import db, setup_db, Issue, Comment, User

#----------------------------------------------------------------------------#
# Example auth headers for RBAC
#----------------------------------------------------------------------------#

test_auth_headers = {
    "admin": {
        'Authorization': os.environ.get('ADMIN_TOKEN_TEST')
    },
    "commenter": {
        'Authorization': os.environ.get('COMMENTER_TOKEN_TEST')
    }
}

#----------------------------------------------------------------------------#
# Seed test database with test entries
#----------------------------------------------------------------------------#


def insert_db_test_records():
    datetime = '2021-04-16 00:00:00.000'

    admin = User(
        id="1",
        username='testadmin',
        name='admin',
        email='admin@admin.com',
        date_joined=datetime,
        last_login=datetime,
        roles=['Admin']
    )

    commenter = User(
        id="2",
        username='testcommenter',
        name='commenter',
        email='commenter@commenter.com',
        date_joined=datetime,
        last_login=datetime,
        roles=['Commenter']
    )

    issue = Issue(
        id=1,
        title='issue',
        text='issue text',
        created_at=datetime,
        user_id=1
    )

    comment = Comment(
        id=1,
        text='comment',
        created_at=datetime,
        user_id=1,
        issue_id=1
    )

    try:
        admin.insert()
        commenter.insert()
        issue.insert()
        comment.insert()
    except Exception as e:
        print('ERROR inserting test db entries >>> ', e)

#----------------------------------------------------------------------------#
# Setup of Unittest
#----------------------------------------------------------------------------#


class TrackerTestCase(unittest.TestCase):
    """This class represents the tracker test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.app = create_app()
        self.client = self.app.test_client

        setup_db(self.app, os.environ['DATABASE_URL_TEST'])

        db.create_all()
        insert_db_test_records()

    def tearDown(self):
        """Executed after reach test"""
        db.session.remove()
        db.drop_all()
        pass

    #----------------------------------------------------------------------------#
    # TESTS
    #----------------------------------------------------------------------------#
    def test(self):
        res = self.client().get('/issues')

        data = json.loads(res.data)

        print(data['issues'])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['issues'])


# From src directory, run 'python test_api.py' to start tests
if __name__ == "__main__":
    unittest.main()
