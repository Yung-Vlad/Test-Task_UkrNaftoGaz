from fastapi import HTTPException, Depends, status, Response, Request, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

import secrets
from datetime import timedelta

from database.users import create_user, get_user, get_statistics
from database.general import check_existing_email
from secure.tokens import JWT, CSRF
from models.users import UserCreateModel
from secure.validating import Validator
from secure.hashing import Hasher


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/signup",
             summary="Registration new user")
def signup(request: Request, user: UserCreateModel) -> dict:
    if check_logged(request):
        return { "message": "First you need to logout" }

    # Check username
    existing_user = get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already busy!")

    # Check password
    password_error = Validator.check_password_complexity(user.password)
    if password_error is not None:
        raise HTTPException(status_code=400, detail=password_error)

    # Check existing email
    existing_email = check_existing_email(user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already busy!")

    # Check valid email
    if not Validator.check_valid_email(user.email):
        raise HTTPException(status_code=400, detail="Email isn't valid!")

    # Hash password and register new user
    user.password = Hasher.get_password_hash(user.password)
    create_user(user)

    return { "message": "User registered successfully" }


@router.post("/signin",
             summary="Authentication user")
def login(request: Request, response: Response, data: OAuth2PasswordRequestForm = Depends()) -> dict:
    if check_logged(request):
        return { "message": "You already logged" }

    user = get_user(data.username)

    # Check username and password
    if not user or not Hasher.verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password!",
            headers={ "WWW-Authenticate": "Bearer" }
        )

    # Create jwt access token
    access_token_expires = timedelta(minutes=JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWT.create_access_token({ "sub": user["username"] },
                                       access_token_expires)

    # Create csrf token
    csrf_token = secrets.token_hex(16)

    # Set jwt to HttpOnlyCookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * JWT.ACCESS_TOKEN_EXPIRE_MINUTES,
        samesite="lax"
    )

    # Set csrf to cookie
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        samesite="lax"
    )

    return { "message": "Login successfully 😉" }

@router.delete("/logout",
             summary="Logout from service")
def logout(request: Request, response: Response) -> dict:
    if check_logged(request):  # If user is logged in
        response.delete_cookie("access_token")
        response.delete_cookie("csrf_token")
        return { "message": "Logged out" }
    else:
        return { "message": "You aren't logged yet!" }

@router.get("/statistics",
            summary="Get activity statistics",
            description="Getting statistics about user activity by id")
def statistics(curr_user: dict = Depends(JWT.get_current_user),
               _ = Depends(CSRF.verify_csrf_token)) -> dict:
    user_id = curr_user["id"]

    return get_statistics(user_id)

# Check if user logged
def check_logged(request: Request) -> bool:
    return bool(request.cookies.get("access_token"))
