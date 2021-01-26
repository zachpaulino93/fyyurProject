import os




SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# I have my own database running on a rasberry pi inside my home that I am connecting too (dummy password)
SQLALCHEMY_DATABASE_URI = 'postgres://pi:20202020@192.168.1.70:5432/fyyurdata'
