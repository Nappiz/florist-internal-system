from models.audit_log_model import AuditLog
from sqlalchemy import inspect


def record(db, actor, action, entity_type, entity_id, details=None):
    user = getattr(actor, 'user', actor)
    identity=inspect(user).identity if user is not None else None
    entry = AuditLog(actor_id=identity[0] if identity else (user.id if user else None),action=action,entity_type=entity_type,entity_id=entity_id,details=details)
    db.add(entry)
    return entry
