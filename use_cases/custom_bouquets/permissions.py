from fastapi import HTTPException

def require_superadmin(actor):
    if actor is None or actor.user.role!="superadmin":
        raise HTTPException(403,"Hanya superadmin dapat mengubah harga atau pengaturan buket.")
