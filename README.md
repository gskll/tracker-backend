# Issue Tracker API

The backend REST API for an issue tracker app, written in python (Flask) and using Auth0 for user authentication.

Deployed on heroku: [https://tracker-gskll.herokuapp.com](https://tracker-gskll.herokuapp.com/)

The endpoints follow REST principles to allow CRUD operations for issues and comments on those issues.

Users are either `admin` with full permissions or `commenter` with basic permissions allowing them to read an issue and add/edit comments.

As user authentication is handled by Auth0, an Auth0 rule fires on each authentication attempt which will add/update a user in our local database, in order to easily access the issues/comments associated with that user.A

The only endpoint that works with no authentication is `GET /issues`
Test it here:

```
curl --request GET 'https://tracker-gskll.herokuapp.com/issues'
```

## Goals

- Architect relational database models in Python
- Utilize SQLAlchemy to conduct database queries
- Follow RESTful principles of API development
- Structure endpoints to respond to four HTTP methods, including error handling
- Enable Role Based Authentication and roles-based access control (RBAC) in a Flask application
- Demonstrate validity of API behavior
- Configure third-party authentication systems
- Configure roles-based access control (RBAC)
- Extend third-party authentication using custom rules

## Stack

- [Python 3.7.10]
- [Flask - Web Framework]
- [SQLAlchemy ORM]
- [PostgresSQL 13.2]
- [Flask - Migrate]
- Authentication - JSON Web Token (JWT) with Auth0
- Python virtual environment - [venv]
- Testing - Unittest
- API testing with [Postman]
- Deployment on [Heroku]

## Local setup

**Assumes PostgreSQL is running locally**

**1. Clone repo**

```bash
git clone https://github.com/gskll/tracker-backend.git
```

**2. Setup virtual environment**

```bash
virtualenv env
source env/Scripts/activate # for windows
source env/bin/activate # for MacOs
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create databases**

```bash
createdb tracker # for Postman/curl testing
createdb tracker-test # for automated test suite
```

**5. Migrate and populate `tracker` database**

```bash
python manage.py db upgrade
psql -d tracker -f example_db.psql
```

**6. Setup environment variables**

See Authentication below get up-to-date JWT tokens

```bash
source setup.sh
```

**7. Run Flask**

```bash
flask run --reload
```

## API Overview

### Authentication

Visit this link to login: [LOGIN](https://gskll.eu.auth0.com/authorize?audience=tracker&response_type=token&client_id=hLGXqFeHV69YJpoqQcALFXoRIF9PGvM0&redirect_uri=https://tracker-gskll.herokuapp.com/)

Visit this link to logout: [LOGOUT](https://gskll.eu.auth0.com/v2/logout?client_id=hLGXqFeHV69YJpoqQcALFXoRIF9PGvM0&returnTo=https://tracker-gskll.herokuapp.com/logout)

**Admin user**

Username: `admin@tracker.com`

Password: `TrackER798`

**Commenter user**

Username: `commenter@tracker.com`

Password: `TrackER798`



Once logged in, the URL will look like this

`https://tracker-gskll.herokuapp.com/#access_token=TOKEN&expires_in=86400&token_type=Bearer`

Take the TOKEN part of the URL and paste it to the relevant variable in `setup.sh` to access the API as that user

### Roles and authentication

- `admin` role
   - `get:issue`
   - `post:issues`
   - `post:comments`
   - `patch:issues`
   - `patch:comments`
   - `delete:issues`
   - `delete:comments`
 - `commenter` role
    - `get:issue`
    - `post:comments`
    - `patch:comments`
    - `delete:comments`

### Endpoints

**View all endpoints and examples request/responses in Postman using the `Issue Tracker.postman_collection.json` collection**

#### LOCAL ONLY: POST `/users`

Posts a new user to the local database

- **Authentication required**: *no*

- **Permissions required**: *none*

- **Request parameters**: JSON body
- **Response type**: JSON

#### LOCAL ONLY: PATCH `/users`

Update a user in the local database

- **Authentication required**: *no*

- **Permissions required**: *none*

- **Request parameters**: JSON body
- **Response type**: JSON

#### GET `/issues`

Retrieves all issues

- **Authentication required**: *no*

- **Permissions required**: *none*

- **Request parameters**: *none*
- **Response type**: JSON

#### GET `/issues/<int:id>`

Retrieves a single issue with all associated comments

- **Authentication required**: yes

- **Permissions required**: `get:issue`

- **Request parameters**: `<int:id>`
- **Response type**: JSON

#### POST `/issues`

Adds a new issue

- **Authentication required**: yes

- **Permissions required**: `post:issues`

- **Request parameters**: JSON body
- **Response type**: JSON

#### POST `/comments`

Adds a new comment

- **Authentication required**: yes

- **Permissions required**: `post:comments`

- **Request parameters**: JSON body
- **Response type**: JSON

#### PATCH `/issues/<int:id>`

Updates a given issue

- **Authentication required**: yes

- **Permissions required**: `patch:issues`

- **Request parameters**: `<int:id>`
- **Response type**: JSON

#### PATCH `/comments/<int:id>`

Updates a given comment

- **Authentication required**: yes

- **Permissions required**: `patch:comments`

- **Request parameters**: `<int:id>`
- **Response type**: JSON

#### DELETE `/issues/<int:id>`

Deletes a given issue

- **Authentication required**: yes

- **Permissions required**: `delete:issues`

- **Request parameters**: `<int:id>`
- **Response type**: JSON

#### DELETE `/comments/<int:id>`

Deletes a given comment

- **Authentication required**: yes

- **Permissions required**: `delete:comments`

- **Request parameters**: `<int:id>`
- **Response type**: JSON

## Testing

### Local testing

```
export ACCEPTED_HOST="localhost"
python test_api.py
```

`source setup.sh` once done with testing use application locally again

### Live testing

Test from Postman

Note: running the full collection will result in failures due to database constraints but each endpoint works if you change the id