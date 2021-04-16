import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import setup_db, Issue, Comment, User
# from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# ROUTES
'''
  POST /users
    it should be a public endpoint
    it should create a new row in the Users table
  returns status code 200 and json {"success": True, "user": user} where user is the newly created user
    or appropriate status code indicating reason for failure
'''


@app.route('/users', methods=['POST'])
def post_users():
    body = request.get_json()

    for field in body.values():
        if not field:
            abort(400)

    user_raw = body.get('user')

    print(user_raw)
    print(user_raw.get('id'))
    print(user_raw['id'])

    # user = User(
    #   id=user_raw['user_id'],
    #   username=user_raw['']
    # )

    # print(user)
    return jsonify({
        'success': True,
        'user': user
    })

    # drink = Drink(title=body.get('title'), recipe=recipe_json)

    # try:
    #     drink.insert()
    # except Exception as e:
    #     print('POST /drinks EXCEPTION >>> ', e)
    #     abort(422)
    # else:
    #     return jsonify({
    #         'success': True,
    #         'drinks': [drink.long()]
    #     })


'''
  GET /issues
    it should be a public endpoint
    it should contain only the issue.format_no_comments() data representation
  returns status code 200 and json {"success": True, "issues": issues} where issues is the list of issues
    or appropriate status code indicating reason for failure
'''


@app.route('/issues', methods=['GET'])
def get_issues():
    issues = Issue.query.order_by(Issue.id).all()
    issues = [issue.format_no_comments() for issue in issues]

    return jsonify({
        "success": True,
        "issues": issues
    })


'''
  GET /issues/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should be a public endpoint
    it should contain only the issue.format_with_comments() data representation
  returns status code 200 and json {"success": True, "issue": issue} where issue is the issue with id of <id>
    or appropriate status code indicating reason for failure
'''

'''
  POST /issues
    it should create a new row in the issues table
    it should be require the 'post:issues' permission
    it should contain the issue.format_no_comments() data representation
  returns status code 200 and json {"success": True, "issue": issue} where issue is the newly created issue
    or appropriate status code indicating reason for failure
'''

'''
  POST /comments
    it should create a new row in the comments table
    it should be require the 'post:comments' permission
    it should contain the comment.format() data representation
  returns status code 200 and json {"success": True, "comment": comment} where comment is the newly created comment
    or appropriate status code indicating reason for failure
'''

'''
  PATCH /issues/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should edit the corresponding row in the issues table
    it should be require the 'patch:issues' permission
    it should contain the issue.format_no_comments() data representation
  returns status code 200 and json {"success": True, "issue": issue} where issue is the edited issue
    or appropriate status code indicating reason for failure
'''


'''
  PATCH /comments/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should edit the corresponding row in the comments table
    it should be require the 'patch:comments' permission
    it should contain the comment.format() data representation
  returns status code 200 and json {"success": True, "comment": comment} where comment is the edited comment
    or appropriate status code indicating reason for failure
'''


'''
  DELETE /issues/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row in the issues table
    it should be require the 'delete:issues' permission
  returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted issue
    or appropriate status code indicating reason for failure
'''

'''
  DELETE /comments/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row in the comments table
    it should be require the 'delete:comments' permission
  returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted comment
    or appropriate status code indicating reason for failure
'''
