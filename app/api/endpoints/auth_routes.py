from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pygments import token
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, TwoFactorVerify, Token
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.services.email_service import send_2fa_email
from app.schemas.user_schema import PasswordResetRequest, PasswordResetConfirm

router = APIRouter(tags=["Authentication"])

security = HTTPBearer()

async def get_current_user(db: Session = Depends(get_db), auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependência atualizada para usar HTTPBearer.
    """
    token = auth.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.email == user_in.email).first()
    if user_exists:
        raise HTTPException(
            status_code=400, 
            detail="Este e-mail já está cadastrado no PrecedentIA."
        )
    
    new_user = User(
        email=user_in.email,
        password=hash_password(user_in.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Usuário criado com sucesso! Faça login para validar seu acesso."}

@router.post("/login")
async def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    
    if not user or not verify_password(user_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
    
    try:
        verification_code = await send_2fa_email(user.email)
        
        user.two_factor_code = verification_code
        user.two_factor_expires = datetime.utcnow() + timedelta(minutes=10)
        
        db.commit()
        
        return {
            "message": "Código de verificação enviado para seu e-mail.",
            "email": user.email 
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao enviar e-mail de autenticação: {str(e)}"
        )
    
@router.post("/verify", response_model=Token)
async def verify_2fa(data: TwoFactorVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if not user.two_factor_code or user.two_factor_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Código de verificação inválido."
        )

    if datetime.utcnow() > user.two_factor_expires:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="O código expirou. Solicite um novo login."
        )

    user.two_factor_code = None
    user.two_factor_expires = None
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Endpoint protegido que retorna os dados do perfil do usuário logado.
    """
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Sinaliza o logout. No Flutter, o token deve ser deletado do Secure Storage.
    """
    return {"message": "Logout realizado com sucesso. Até logo!"}

@router.post("/password-reset/request")
async def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "Caso o email exista, um código foi enviado."}
    
    code = await send_2fa_email(user.email)
    user.two_factor_code = code
    user.two_factor_expires = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    
    return {"message": "Código de recuperação enviado para seu e-mail."}

@router.post("/password-reset/confirm")
async def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or user.two_factor_code != data.code:
        raise HTTPException(status_code=400, detail="Código inválido ou e-mail incorreto.")
    
    if datetime.utcnow() > user.two_factor_expires:
        raise HTTPException(status_code=400, detail="Código expirado.")
    
    user.password = hash_password(data.new_password)
    user.two_factor_code = None
    user.two_factor_expires = None
    db.commit()
    
    return {"message": "Senha alterada com sucesso! Agora você pode fazer login."}