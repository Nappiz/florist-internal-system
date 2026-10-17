from sqlalchemy import func, select

from models.audit_log_model import AuditLog


def list_entries(db, query, start, end):
    statement = select(AuditLog).where(AuditLog.created_at >= start, AuditLog.created_at < end)
    for field in ("actor_id", "action", "entity_type", "entity_id"):
        value = getattr(query, field)
        if value is not None:
            statement = statement.where(getattr(AuditLog, field) == value)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    rows = db.scalars(statement.order_by(AuditLog.created_at.desc(), AuditLog.id).limit(query.limit).offset(query.offset)).all()
    return rows, total
