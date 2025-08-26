from functools import wraps
from sqlalchemy.orm import sessionmaker
import contextvars
from ..config.connection_engine import connection_engine

# --------------------------------------------------------------------
# Context variable to store the current database session.
# This ensures a session can be passed implicitly across function calls
# without explicitly threading it through arguments.
# --------------------------------------------------------------------
db_session_context = contextvars.ContextVar("db_session_context", default=None)

def transactional(func):
    """
    Decorator to wrap functions in a managed SQLAlchemy transaction.
    
    Ensures that:
    - If a session already exists in context, it is reused.
    - Otherwise, a new session is created, committed, and closed.
    - On errors, the session is rolled back and closed.
    
    Parameters
    ----------
    func : callable
        The function to wrap. It must accept a `session` keyword argument.
    
    Returns
    -------
    callable
        The wrapped function, executed within a database transaction.
    
    Example
    -------
    >>> @transactional
    ... def create_user(user: User, session=None):
    ...     session.add(user)
    ...     return user
    ...
    >>> new_user = create_user(User(...))
    """
    @wraps(func)
    def wrap_func(*args, **kwargs):
        # Try to get an existing session from context
        session = db_session_context.get()
        if session:
            return func(*args, session=session, **kwargs)

        # Create a new session if none exists
        session = sessionmaker(bind=connection_engine)()
        db_session_context.set(session)

        try:
            # Run the wrapped function with session
            result = func(*args, session=session, **kwargs)
            session.flush()   # Push pending changes
            session.commit()  # Commit transaction
        except Exception as e:
            session.rollback()  # Rollback on failure
            raise e
        finally:
            session.close()
            db_session_context.set(None)  # Clear context

        return result

    return wrap_func
