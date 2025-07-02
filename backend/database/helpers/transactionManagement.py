from functools import wraps
from sqlalchemy.orm import sessionmaker
import contextvars
from ..config.connection_engine import connection_engine

db_session_context = contextvars.ContextVar("db_session_context",default=None)

def transactional(func):
    @wraps(func)
    def wrap_func(*args,**kwargs):
        session = db_session_context.get()
        if session:
            return func(*args,session=session,**kwargs)
        
        session = sessionmaker(bind=connection_engine)()
        db_session_context,set(session)

        try:
            result = func(*args,session=session,**kwargs)
            session.flush()
            session.commit()
        
        except Exception as e:
            session.rollback()
            raise e
        
        finally:
            session.close()
            db_session_context.set(None)

        return result
    
    return wrap_func