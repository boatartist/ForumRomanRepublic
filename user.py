from base import Base
from sqlalchemy import select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
import hashlib
import datetime
from exceptions import PermissionDenied 

def hash_pwd(pwd):
    salt = 'ABC123#@!'
    return hashlib.sha256((pwd+salt).encode()).hexdigest()

def find_user_from_id(id, session):
    return session.query(User).filter_by(id=id).first()

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key = True)
    email: Mapped[str]
    pwd_hash: Mapped[str]
    fname: Mapped[str]
    lname: Mapped[str]
    birth_year: Mapped[int]
    birth_month: Mapped[int]
    birth_day: Mapped[int]

    def __init__(self, email, pwd, fname, lname, year, month, day):
        self.email = email.lower()
        self.pwd_hash = hash_pwd(pwd)
        self.fname = fname
        self.lname = lname
        self.birth_year = year
        self.birth_month = month
        self.birth_day = day
        if not self.check_birthday():
            raise PermissionDenied

    def check_email(self, email):
        '''
        Checks if this is a vaild email
        '''
        if self.email == email.lower():
            return True
        else:
            return False
        
    def check_pwd(self, pwd):
        '''
        Given un-hashed password, check if it is valid for login
        '''
        hashed = hash_pwd(pwd)
        if hashed == self.pwd_hash:
            return True
        else:
            return False
    
    def update_pwd(self, new_pwd):
        '''
        Replace old password with new hashed password
        '''
        hashed = hash_pwd(new_pwd)
        self.pwd_hash = hashed

    def get_name(self):
        return f'{self.fname} {self.lname}'
    
    def get_id(self):
        return self.id
    
    def get_email(self):
        return self.email
    
    def check_birthday(self):
        current_date = datetime.datetime.now()
        birthdate = datetime.datetime(self.birth_year, self.birth_month, self.birth_day)
        age = current_date - birthdate
        if age.days >= 16*365: # age is a datetime.timedelta object and only has days, check if age is more than 16*365 days
            return True
        else:
            return False