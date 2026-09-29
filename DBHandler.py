import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()


class DBHandler:
    Base = declarative_base()
    server = os.getenv('DB_SERVER', 'localhost,1433')
    database = os.getenv('DB_NAME', 'IndustrialWatchFYP')
    username = os.getenv('DB_USER', 'sa')
    password = os.getenv('DB_PASSWORD', '')
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server')
    echo = os.getenv('DB_ECHO', 'false').lower() == 'true'
    _engine = None

    def __init__(self):
        if DBHandler._engine is None:
            odbc = (f'DRIVER={{{DBHandler.driver}}};SERVER={DBHandler.server};DATABASE={DBHandler.database};'
                    f'UID={DBHandler.username};PWD={DBHandler.password};TrustServerCertificate=yes')
            DBHandler._engine = create_engine(f'mssql+pyodbc:///?odbc_connect={quote_plus(odbc)}',
                                              echo=DBHandler.echo)
        self.engine = DBHandler._engine
        self.Session = sessionmaker(bind=self.engine)


def return_session():
    db_handler = DBHandler()
    return db_handler.Session()


def check_database_connection():
    try:
        if DBHandler().engine.connect():
            print("Database connection successful.")
        else:
            print("Database is not Connected")
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        exit()
