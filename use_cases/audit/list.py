from fastapi import HTTPException

from crud import audit_crud
from use_cases.reports.period import resolve_period


def _redact(value):
    sensitive = ("password", "token", "secret", "cookie", "authorization", "credential")
    if isinstance(value, dict):
        return {key: _redact(item) for key, item in value.items() if not any(word in key.lower() for word in sensitive)}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def list_audit(db, actor, query):
    if not actor.user.is_superadmin:
        raise HTTPException(403, "Hanya superadmin dapat melihat audit log global.")
    period, start, end = resolve_period(query)
    rows, total = audit_crud.list_entries(db, query, start, end)
    return {"period": period, "items": [{"id": row.id, "actor_id": row.actor_id, "action": row.action,
        "entity_type": row.entity_type, "entity_id": row.entity_id, "details": _redact(row.details), "created_at": row.created_at} for row in rows],
        "total": total, "limit": query.limit, "offset": query.offset}
