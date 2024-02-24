# Flask_Backend

> .flaskenv

```
shell
FLASK_APP   = app
FLASK_ENV   = development
FLASK_DEBUG = 1
```

> .env

```
shell
SECRET_KEY                = e68a56aaa9da4738968840caa16cb63e
JWT_SECRET_KEY            = 76b93f66f1e041f78deefde9cbe66d63
DATABASE_URI              = mysql%3A//root%3AWlj%2B%3D9351524%40120.24.177.83%3A3306/my_db
JWT_ACCESS_TOKEN_EXPIRES  = 30
JWT_REFRESH_TOKEN_EXPIRES = 1
REDIS_URL                 = redis%3A//default%3AWlj%2B%3D9351524%40120.24.177.83%3A6379/0
MAX_ALLOWED_SIZE          = 5242880
IMG_DIR                   = /etc
CELERY_BROKER_URL         = redis%3A//default%3AWlj%2B%3D9351524%40120.24.177.83%3A6379/0
CELERY_RESULT_BACKEND     = redis%3A//default%3AWlj%2B%3D9351524%40120.24.177.83%3A6379/0
```

> requirements.txt

```
shell
aniso8601==9.0.1
blinker==1.7.0
click==8.1.7
colorama==0.4.6
Faker==23.2.1
Flask==3.0.2
Flask-Cors==4.0.0
Flask-JWT-Extended==4.6.0
Flask-RESTful==0.3.10
Flask-SQLAlchemy==3.1.1
greenlet==3.0.3
itsdangerous==2.1.2
Jinja2==3.1.3
MarkupSafe==2.1.5
mysqlclient==2.2.4
PyJWT==2.8.0
PyMySQL==1.1.0
python-dateutil==2.8.2
python-dotenv==1.0.1
pytz==2024.1
six==1.16.0
SQLAlchemy==2.0.27
typing_extensions==4.9.0
Werkzeug==3.0.1

```

>  run

```
shell
cd /Flask_Backend
env\Script\activate        # NT
source env/bin/activate    # Linux
pip install -m requirements.txt    # 首次运行
flask run
```
