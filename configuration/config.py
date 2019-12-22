import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

SECRET_KEY=os.getenv('SECRET_KEY')