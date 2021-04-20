import os
import json
from datetime import datetime

from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from flask_cors import CORS

from .models import setup_db, Issue, Comment, User
from .auth import AuthError, requires_auth


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    # CORS Headers
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    #----------------------------------------------------------------------------#
    #
    # ROUTES
    #
    #----------------------------------------------------------------------------#

    #----------------------------------------------------------------------------#
    #  POST /users
    #    it should only be called from the Auth0 authentication rule, or localhost:5000 for testing
    #    it should be a public endpoint
    #    it should add a row in the Users table
    #  returns status code 200 and json {"success": True, "user": user} where user is the newly created user
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/users', methods=['POST'])
    def add_user():
        if request.environ.get('HTTP_HOST') != os.environ.get('ACCEPTED_HOST'):
            abort(401)

        body = request.get_json()

        for field in body.values():
            if not field:
                abort(400)

        user_dict = body.get('user')
        auth_id = user_dict.get('user_id')

        if not auth_id:
            print('400: no user_id provided')
            abort(400)

        user_exists = User.query.filter_by(auth_id=auth_id).one_or_none()

        if user_exists:
            print('422: user already exists')
            abort(422)

        user = User(
            auth_id=auth_id,
            nickname=user_dict.get('nickname'),
            name=user_dict.get('name'),
            email=user_dict.get('email'),
            created_at=user_dict.get('created_at'),
            last_login=user_dict.get('created_at'),
            roles=body.get('roles')
        )

        try:
            user.insert()
        except Exception as e:
            print('POST /users EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'user': user.format_short(),
            })

    #----------------------------------------------------------------------------#
    #  PATCH /users
    #    it should only be called from the Auth0 authentication rule, or localhost:5000 for testing
    #    it should be a public endpoint
    #    it should update a row in the Users table with any new information
    #  returns status code 200 and json {"success": True, "user": user} where user is the newly created user
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/users', methods=['PATCH'])
    def update_user():
        if request.environ.get('HTTP_HOST') != os.environ.get('ACCEPTED_HOST'):
            abort(401)

        body = request.get_json()

        user_dict = body.get('user')

        if user_dict is None:
            abort(422)

        auth_id = user_dict.get('user_id')
        user = User.query.filter_by(auth_id=auth_id).one_or_none()

        if user is None:
            abort(404)

        for field in user_dict:
            if user[field] and user[field] != user_dict[field]:
                user[field] = user_dict[field]

        new_roles = body.get('roles')

        if new_roles is None:
            abort(422)

        if user.roles != new_roles:
            user.roles = new_roles

        user.last_login = datetime.now()

        try:
            user.update()
        except Exception as e:
            print('PATCH /users EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'user': user.format_short()
            })

    #----------------------------------------------------------------------------#
    #  GET /issues
    #    it should be a public endpoint
    #    it should contain only the issue.format_no_comments() data representation
    #  returns status code 200 and json {"success": True, "issues": issues} where issues is the list of issues
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/issues', methods=['GET'])
    def get_issues():
        issues = Issue.query.order_by(Issue.id).all()
        issues = [issue.format_no_comments() for issue in issues]

        return jsonify({
            "success": True,
            "issues": issues
        })

    #----------------------------------------------------------------------------#
    #  GET /issues/<id>
    #    where <id> is the existing model id
    #    it should respond with a 404 error if <id> is not found
    #    it should be a public endpoint
    #    it should contain only the issue.format_with_comments() data representation
    #  returns status code 200 and json {"success": True, "issue": issue} where issue is the issue with id of <id>
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/issues/<id>', methods=['GET'])
    @requires_auth('get:issue')
    def get_issue(auth_payload, id):
        issue = Issue.query.get(id)

        if not issue:
            print('No issue found')
            abort(404)

        issue = issue.format_with_comments()

        return jsonify({
            "success": True,
            "issue": issue
        })

    #----------------------------------------------------------------------------#
    #  POST /issues
    #    it should create a new row in the issues table
    #    it should be require the 'post:issues' permission
    #    it should contain the issue.format_no_comments() data representation
    #  returns status code 200 and json {"success": True, "issue": issue} where issue is the newly created issue
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/issues', methods=['POST'])
    @requires_auth('post:issues')
    def post_issue(auth_payload):
        body = request.get_json()

        for field in body.values():
            if not field:
                abort(400)

        issue = Issue(
            title=body.get('title'),
            text=body.get('text'),
            created_at=datetime.now(),
            user_id=body.get('user_id')
        )

        try:
            issue.insert()
        except Exception as e:
            print('POST /issues EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'issue': issue.format_no_comments()
            })

    #----------------------------------------------------------------------------#
    #  POST /comments
    #    it should create a new row in the comments table
    #    it should be require the 'post:comments' permission
    #    it should contain the comment.format() data representation
    #  returns status code 200 and json {"success": True, "comment": comment} where comment is the newly created comment
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/comments', methods=['POST'])
    @requires_auth('post:comments')
    def post_comment(auth_payload):
        body = request.get_json()

        for field in body.values():
            if not field:
                abort(400)

        comment = Comment(
            text=body.get('text'),
            created_at=datetime.now(),
            user_id=body.get('user_id'),
            issue_id=body.get('issue_id')
        )

        try:
            comment.insert()
        except Exception as e:
            print('POST /comments EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'comment': comment.format()
            })

    #----------------------------------------------------------------------------#
    # PATCH /issues/<id>
    #    where < id > is the existing model id
    #    it should respond with a 404 error if < id > is not found
    #    it should edit the corresponding row in the issues table
    #    it should be require the 'patch:issues' permission
    #    it should contain the issue.format_no_comments() data representation
    #  returns status code 200 and json {"success": True, "issue": issue} where issue is the edited issue
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/issues/<id>', methods=['PATCH'])
    @requires_auth('patch:issues')
    def patch_issues(auth_payload, id):
        issue = Issue.query.get(id)
        body = request.get_json()

        if not issue:
            abort(404)

        if not body:
            abort(400)

        if 'title' in body:
            issue.title = body.get('title')

        if 'text' in body:
            issue.text = body.get('text')

        if 'open' in body:
            issue.open = body.get('open')

            if not body.get('open'):
                issue.closed_at = datetime.now()

        issue.last_modified = datetime.now()

        try:
            issue.update()
        except Exception as e:
            print('PATCH /issues/<id> EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'issue': issue.format_no_comments()
            })

    #----------------------------------------------------------------------------#
    #  PATCH /comments/<id>
    #    where <id> is the existing model id
    #    it should respond with a 404 error if <id> is not found
    #    it should edit the corresponding row in the comments table
    #    it should be require the 'patch:comments' permission
    #    it should contain the comment.format() data representation
    #  returns status code 200 and json {"success": True, "comment": comment} where comment is the edited comment
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/comments/<id>', methods=['PATCH'])
    @requires_auth('patch:comments')
    def patch_comments(auth_payload, id):
        comment = Comment.query.get(id)
        body = request.get_json()

        if not comment:
            abort(404)

        if not body:
            abort(400)

        if 'text' in body:
            comment.text = body.get('text')

        comment.last_modified = datetime.now()

        try:
            comment.update()
        except Exception as e:
            print('PATCH /comments/<id> EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'comment': comment.format()
            })

    #----------------------------------------------------------------------------#
    #  DELETE /issues/<id>
    #    where <id> is the existing model id
    #    it should respond with a 404 error if <id> is not found
    #    it should delete the corresponding row in the issues table
    #    it should be require the 'delete:issues' permission
    #  returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted issue
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/issues/<id>', methods=['DELETE'])
    @requires_auth('delete:issues')
    def delete_issues(auth_payload, id):
        issue = Issue.query.get(id)

        if not issue:
            abort(404)

        try:
            issue.delete()
        except Exception as e:
            print('DELETE /issues/<issue_id> EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'delete': id
            })

    #----------------------------------------------------------------------------#
    #  DELETE /comments/<id>
    #    where <id> is the existing model id
    #    it should respond with a 404 error if <id> is not found
    #    it should delete the corresponding row in the comments table
    #    it should be require the 'delete:comments' permission
    #  returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted comment
    #    or appropriate status code indicating reason for failure
    #----------------------------------------------------------------------------#

    @app.route('/comments/<id>', methods=['DELETE'])
    @requires_auth('delete:comments')
    def delete_comments(auth_payload, id):
        comment = Comment.query.get(id)

        if not comment:
            abort(404)

        try:
            comment.delete()
        except Exception as e:
            print('DELETE /comments/<comment_id> EXCEPTION >>> ', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'delete': id
            })

    #----------------------------------------------------------------------------#
    # Error Handling
    #----------------------------------------------------------------------------#

    @app.errorhandler(AuthError)
    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(422)
    def error_handler(error):
        return jsonify({
            'success': False,
            'error': error.code,
            'message': error.description
        }), error.code

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
