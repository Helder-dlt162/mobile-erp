from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import hash_password
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Usuários"])


def require_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem gerenciar usuários")


@router.get("", response_model=list[UserRead])
def list_users(user: CurrentUser, db: DbSession) -> list[User]:
    require_admin(user)
    return list(db.scalars(select(User).order_by(User.name)).all())


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, user: CurrentUser, db: DbSession) -> User:
    require_admin(user)
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    created = User(name=payload.name, email=payload.email.lower(), password_hash=hash_password(payload.password), role="operador", permissions=payload.permissions)
    db.add(created)
    db.commit()
    db.refresh(created)
    return created


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, user: CurrentUser, db: DbSession) -> User:
    require_admin(user)
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    duplicate = db.scalar(select(User).where(User.email == payload.email.lower(), User.id != user_id))
    if duplicate:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    target.name = payload.name
    target.email = payload.email.lower()
    target.permissions = payload.permissions
    target.is_active = payload.is_active
    if payload.password:
        target.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(target)
    return target


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(user_id: int, user: CurrentUser, db: DbSession) -> None:
    require_admin(user)
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if target.id == user.id:
        raise HTTPException(status_code=409, detail="O usuário atual não pode ser desativado")
    target.is_active = False
    db.commit()