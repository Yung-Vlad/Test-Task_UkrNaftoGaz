from fastapi import APIRouter, Depends

from models.users import PermissionModel
import database.accesses as db
from secure.tokens import JWT, CSRF


router = APIRouter(prefix="/accesses", tags=["Accesses"])

@router.post("/set-permission",
             summary="Set permission to your notes",
             description="Set permissions to your notes to be shared other users")
def set_permission(permission: PermissionModel,
                   curr_user: dict = Depends(JWT.get_current_user),
                   _ = Depends(CSRF.verify_csrf_token)) -> dict:

    curr_user_id = curr_user["id"]
    if curr_user_id == permission.user_id:  # If user enters his id
        return { "message": "You can't give access to yourself!" }

    return db.set_permission(permission, curr_user_id)

@router.delete("/delete-permission",
               summary="Delete permission to your notes",
               description="Delete permission to your notes to be shared other users")
def delete_permission(permission: PermissionModel,
                      curr_user: dict = Depends(JWT.get_current_user),
                      _ = Depends(CSRF.verify_csrf_token)) -> dict:

    curr_user_id = curr_user["id"]
    if curr_user_id == permission.user_id:  # If user enters his id
        return { "message": "You can't take access away from yourself!" }

    return db.delete_permission(permission, curr_user_id)
