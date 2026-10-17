from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.hashing import hash_password
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ─── 1. ME ENDPOINT (Statik yo'l - Eng yuqorida turishi shart!) ────
@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/me/password")
def change_password(
    pass_data: schemas.PasswordChangeSchema, # type: ignore
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {"message": "Parol muvaffaqiyatli o'zgartirildi"}


# ─── 3. CREATE USER ──────────────────────────────────────────────
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Email allaqachon borligini tekshirish
    existing = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email allaqachon ro'yxatdan o'tgan"
        )

    # Parolni xashlash
    hashed = hash_password(user.password)
    user.password = hashed

    new_user = models.User(**user.model_dump()) # Agar Pydantic v2 bo'lsa model_dump(), v1 bo'lsa dict()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ─── 4. GET USER (Dinamik yo'l - Har doim pastda turishi kerak!) ──
@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={user_id} bo'lgan foydalanuvchi topilmadi"
        )

    return user