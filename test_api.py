
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
    #
    # TESTS
    #
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    # POST /users Endpoint
    #   - test_add_user: 200 - tests correctly adding a user
    #   - test_add_user_already_exists: 422 - tests adding a pre-existing user
    #----------------------------------------------------------------------------#

    def test_add_user(self):
        test_user_json = {
            "user": {
                "user_id": "test",
                "nickname": 'testuser',
                "name": 'user',
                "email": 'user@user.com',
                "created_at": '2021-04-16 00:00:00.000',
            },
            "roles": ["Admin"]
        }

        prev_user_count = len(User.query.all())

        res = self.client().post('/users', json=test_user_json)
        data = json.loads(res.data)

        curr_user_count = len(User.query.all())

        self.assertEqual(curr_user_count - prev_user_count, 1)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_add_user_already_exists(self):
        test_user_json = {
            "user": {
                "user_id": "test",
                "nickname": 'testuser',
                "name": 'user',
                "email": 'user@user.com',
                "created_at": '2021-04-16 00:00:00.000',
            },
            "roles": ["Admin"]
        }

        res = self.client().post('/users', json=test_user_json)

        prev_user_count = len(User.query.all())

        res = self.client().post('/users', json=test_user_json)

        data = json.loads(res.data)

        curr_user_count = len(User.query.all())

        self.assertEqual(curr_user_count - prev_user_count, 0)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # GET /issues Endpoint
    #   - test_get_issues: 200 - tests that endpoint is working
    #   - test_get_issues_invalid_route: 404 - endpoint only works with /issues
    #----------------------------------------------------------------------------#

    def test_get_issues(self):
        res = self.client().get('/issues')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['issues'])

    def test_get_issues_invalid_route(self):
        res = self.client().get('/issuess')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # GET /issues/<id> Endpoint
    #   - test_get_issue: 200 - tests that admin role can get a single issue
    #   - test_get_issue_invalid_permissions: 401 - tests that public cannot get a single issue
    #   - test_get_issue_invalid_id: 404 - tests fetching invalid id
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    # POST /issues Endpoint
    #   - test_add_issues: 200 - tests that admin role can add issues
    #   - test_add_issues_invalid_permissions: 401 - tests that commenter role cannot add issues
    #   - test_add_issue_non_unique_title: 422 - test uniqueness of issue titles
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    # POST /comments Endpoint
    #   - test_add_comment: 200 - tests that commenter role can add comments
    #   - test_add_comment_invalid_permissions: 401 - tests that public cannot add comments
    #   - test_add_comment_invalid_user_id: 422 - tests that endpoint fails if invalid user_id sent
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    # PATCH /issues Endpoint
    #   - test_update_issue: 200 - tests that admin role can update an issue
    #   - test_update_issues_invalid_permissions: 401 - tests that commenter role cannot update an issue
    #   - test_update_issues_invalid_id: 404 - tests endpoint fails with invalid issue id
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    # PATCH /comments Endpoint
    #   - test_update_comment: 200 - tests that commenter role can update a comment
    #   - test_update_comment_invalid_permissions: 401 - tests that public cannot update a comment
    #   - test_update_comment_invalid_id: 404 - tests endpoint fails with invalid comment id
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    # DELETE /comments Endpoint
    #   - test_delete_comment_invalid_permissions: 401 - tests public cannot delete a comment
    #   - test_delete_comment_invalid_id: 404 - tests endpoint fails with invalid comment id
    #   - test_delete_comment: 200 - tests commenter role can delete a comment
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    # DELETE /issues Endpoint
    #   - test_delete_issue_invalid_permissions: 401 - tests commenter role cannot delete an issue
    #   - test_delete_issue_invalid_id: 404 - tests endpoint fails with invalid issue id
    #   - test_delete_issue: 200 - tests admin role can delete an issue
    #----------------------------------------------------------------------------#


# From src directory, run 'python test_api.py' to start tests
if __name__ == "__main__":
    unittest.main()
