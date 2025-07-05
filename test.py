from sqlalchemy.orm import Session
from backend.database.daos.user_dao import UserDao
from backend.database.entities.user import User
from backend.database.helpers.transactionManagement import transactional

@transactional
# def main(session:Session,username:str):
#     user_dao = UserDao()
#     users = user_dao.fetchUser(session=session,username=username)
#     return users

# print(main(username='admin'))

def updateVerCode(session:Session,username:str,code:str,code_created_on):
    print(username,code,code_created_on)
    user = session.query(User).filter(User.user_name == username).one()
    print(user)

updateVerCode(username='user1',code='',code_created_on='')
