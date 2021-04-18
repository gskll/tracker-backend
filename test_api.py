
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
        id=2,
        title='issue',
        text='issue text',
        created_at=datetime,
        user_id=1
    )

    comment = Comment(
        id=2,
        text='comment',
        created_at=datetime,
        user_id=1,
        issue_id=2
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

        self.test_user_json = {
            "user": {
                "user_id": "test",
                "nickname": 'testuser',
                "name": 'user',
                "email": 'user@user.com',
                "created_at": '2021-04-16 00:00:00.000',
            },
            "roles": ["Admin"]
        }

        self.test_issue_json = {
            "title": "test2",
            "text": "text",
            "created_at": "'2021-04-16 00:00:00.000'",
            "user_id": "1"
        }

        self.test_comment_json = {
            "text": "test comment text",
            "user_id": "1",
            "issue_id": 2
        }

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
        prev_user_count = len(User.query.all())

        res = self.client().post('/users', json=self.test_user_json)
        data = json.loads(res.data)

        curr_user_count = len(User.query.all())

        self.assertEqual(curr_user_count - prev_user_count, 1)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_add_user_already_exists(self):
        res = self.client().post('/users', json=self.test_user_json)

        prev_user_count = len(User.query.all())

        res = self.client().post('/users', json=self.test_user_json)

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

    def test_get_issue(self):
        res = self.client().get(
            '/issues/2',
            headers=test_auth_headers['admin']
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['issue'])
        self.assertEqual(data['issue']['title'], 'issue')

    def test_get_issue_invalid_permissions(self):
        res = self.client().get('/issues/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_get_issue_invalid_id(self):
        res = self.client().get(
            '/issues/100',
            headers=test_auth_headers['admin']
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # POST /issues Endpoint
    #   - test_add_issue: 200 - tests that admin role can add issues
    #   - test_add_issue_invalid_permissions: 403 - tests that commenter role cannot add issues
    #   - test_add_issue_non_unique_title: 422 - test uniqueness of issue titles
    #----------------------------------------------------------------------------#

    def test_add_issue(self):
        res = self.client().post(
            '/issues',
            headers=test_auth_headers['admin'],
            json=self.test_issue_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['issue'])
        self.assertEqual(data['issue']['title'], self.test_issue_json['title'])

    def test_add_issue_invalid_permissions(self):
        res = self.client().post(
            '/issues',
            headers=test_auth_headers['commenter'],
            json=self.test_issue_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_add_issue_non_unique_title(self):
        self.client().post(
            '/issues',
            headers=test_auth_headers['admin'],
            json=self.test_issue_json
        )

        res = self.client().post(
            '/issues',
            headers=test_auth_headers['admin'],
            json=self.test_issue_json
        )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # POST /comments Endpoint
    #   - test_add_comment: 200 - tests that commenter role can add comments
    #   - test_add_comment_invalid_permissions: 401 - tests that public cannot add comments
    #   - test_add_comment_invalid_user_id: 422 - tests that endpoint fails if invalid user_id sent
    #----------------------------------------------------------------------------#

    def test_add_comment(self):
        res = self.client().post(
            '/comments',
            headers=test_auth_headers['commenter'],
            json=self.test_comment_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['comment'])
        self.assertEqual(data['comment']['text'],
                         self.test_comment_json['text'])

    def test_add_comment_invalid_permissions(self):
        res = self.client().post(
            '/comments',
            json=self.test_comment_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    #------------------------------------  b----------------------------------------#
    # PATCH /issues Endpoint
    #   - test_update_issue: 200 - tests that admin role can update an issue
    #   - test_update_issue_invalid_permissions: 403 - tests that commenter role cannot update an issue
    #   - test_update_issue_invalid_id: 404 - tests endpoint fails with invalid issue id
    #----------------------------------------------------------------------------#
    def test_update_issue(self):
        self.test_issue_json['title'] = 'EDITED'

        res = self.client().patch(
            '/issues/2',
            headers=test_auth_headers['admin'],
            json=self.test_issue_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['issue'])
        self.assertEqual(data['issue']['title'], 'EDITED')

    def test_update_issue_invalid_permissions(self):
        self.test_issue_json['title'] = 'EDITED'

        res = self.client().patch(
            '/issues/2',
            headers=test_auth_headers['commenter'],
            json=self.test_issue_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_update_issue_invalid_id(self):
        self.test_issue_json['title'] = 'EDITED'

        res = self.client().patch(
            '/issues/100',
            headers=test_auth_headers['admin'],
            json=self.test_issue_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # PATCH /comments Endpoint
    #   - test_update_comment: 200 - tests that commenter role can update a comment
    #   - test_update_comment_invalid_permissions: 401 - tests that public cannot update a comment
    #   - test_update_comment_invalid_id: 404 - tests endpoint fails with invalid comment id
    #----------------------------------------------------------------------------#
    def test_update_comment(self):
        self.test_comment_json['text'] = 'EDITED'

        res = self.client().patch(
            '/comments/2',
            headers=test_auth_headers['commenter'],
            json=self.test_comment_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['comment'])
        self.assertEqual(data['comment']['text'], 'EDITED')

    def test_update_comment_invalid_permissions(self):
        self.test_comment_json['text'] = 'EDITED'

        res = self.client().patch(
            '/comments/2',
            json=self.test_comment_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_update_comment_invalid_id(self):
        self.test_comment_json['text'] = 'EDITED'

        res = self.client().patch(
            '/comments/100',
            headers=test_auth_headers['admin'],
            json=self.test_comment_json
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # DELETE /comments Endpoint
    #   - test_delete_comment_invalid_permissions: 401 - tests public cannot delete a comment
    #   - test_delete_comment_invalid_id: 404 - tests endpoint fails with invalid comment id
    #   - test_delete_comment: 200 - tests commenter role can delete a comment
    #----------------------------------------------------------------------------#

    def test_delete_comment_invalid_permissions(self):
        res = self.client().delete('/comments/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])

    def test_delete_comment_invalid_id(self):
        res = self.client().delete(
            '/comments/100',
            headers=test_auth_headers['commenter'],
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_comment(self):
        prev_comment_count = len(Comment.query.all())
        res = self.client().delete(
            '/comments/2',
            headers=test_auth_headers['commenter'],
        )
        curr_comment_count = len(Comment.query.all())
        data = json.loads(res.data)

        self.assertEqual(prev_comment_count - curr_comment_count, 1)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['delete'], '2')

    #----------------------------------------------------------------------------#
    # DELETE /issues Endpoint
    #   - test_delete_issue_invalid_permissions: 403 - tests commenter role cannot delete an issue
    #   - test_delete_issue_invalid_id: 404 - tests endpoint fails with invalid issue id
    #   - test_delete_issue: 200 - tests admin role can delete an issue
    #----------------------------------------------------------------------------#

    def test_delete_issue_invalid_permissions(self):
        res = self.client().delete(
            '/issues/2',
            headers=test_auth_headers['commenter'],
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_delete_issue_invalid_id(self):
        res = self.client().delete(
            '/issues/100',
            headers=test_auth_headers['admin'],
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_issue(self):
        res = self.client().post(
            '/issues',
            headers=test_auth_headers['admin'],
            json=self.test_issue_json
        )
        data = json.loads(res.data)

        issue_id = data['issue']['id']

        prev_issue_count = len(Issue.query.all())

        res = self.client().delete(
            f'/issues/{issue_id}',
            headers=test_auth_headers['admin'],
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['delete'], str(issue_id))


# From src directory, run 'python test_api.py' to start tests
if __name__ == "__main__":
    unittest.main()
