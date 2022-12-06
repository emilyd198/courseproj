from pathlib import Path

import os

from flask.cli import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent
env_file_name = ".env"
# env_path = Path.cwd().parent.joinpath(f"{env_file_name}")
env_path = Path.cwd().joinpath(f"{env_file_name}")
load_dotenv(env_path)
print(env_path)
DEBUG = True

DATABASE_URI = 'postgresql://{dbhost}/course_project'.format(
    dbhost=os.environ['DBHOST']
)

TIME_ZONE = 'UTC'
STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATIC_URL = 'static/'
