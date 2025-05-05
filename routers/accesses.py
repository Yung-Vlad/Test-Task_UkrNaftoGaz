from http.client import HTTPException

from fastapi import APIRouter, Depends

from models.users import AccessModel, AccessInternalModel, Permission
import database.accesses as db
from secure.tokens import JWT, CSRF


router = APIRouter(prefix="/accesses", tags=["Accesses"])

@router.post("/set-permission",
             summary="Set permission to your notes",
             description="Set permissions to your notes to be shared other users")
def set_permission(access: AccessModel,
                   permission: Permission = Permission.read,
                   curr_user: dict = Depends(JWT.get_current_user),
                   _ = Depends(CSRF.verify_csrf_token)) -> dict:

    curr_user_id = curr_user["id"]
    if curr_user_id == access.user_id:  # If user enters his id
        return { "message": "You can't give access to yourself!" }


    permission_value = 1 if permission == Permission.read else 2
    access = AccessInternalModel(**access.dict(), permission=permission_value)

    return db.set_permission(access, curr_user_id)

@router.put("/edit-permission",
            summary="Edit permission",
            description="Edit permission for special user to your note")
def edit_permission(access: AccessModel,
                    permission: Permission = Permission.read,
                    curr_user: dict = Depends(JWT.get_current_user),
                    _ = Depends(CSRF.verify_csrf_token)) -> dict:
    curr_user_id = curr_user["id"]
    if curr_user_id == access.user_id:  # If user enters his id
        return {"message": "You can't change permission to yourself!"}

    permission_value = 1 if permission == Permission.read else 2
    access = AccessInternalModel(**access.dict(), permission=permission_value)

    return db.edit_permission(access, curr_user_id)


@router.delete("/delete-permission",
               summary="Delete permission to your notes",
               description="Delete permission to your notes to be shared other users")
def delete_permission(access: AccessModel,
                      curr_user: dict = Depends(JWT.get_current_user),
                      _ = Depends(CSRF.verify_csrf_token)) -> dict:

    curr_user_id = curr_user["id"]
    if curr_user_id == access.user_id:  # If user enters his id
        return { "message": "You can't take access away from yourself!" }

    return db.delete_permission(access, curr_user_id)
