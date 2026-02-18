# from datetime import datetime, timedelta
# from fastapi import APIRouter, HTTPException, status
# from fastapi.params import Depends
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
# from sqlalchemy.orm import Session
# from jose import jwt, JWTError
# # from product import models
# # from product import schemas
# # from product.database import get_db
# # from product.schemas import LoginRequest

# SECRET_KEY = "8ef337392c1ee90ecafa529003619cfc49c4695b53c1855fa819fcdece5a82de"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 20

# router = APIRouter(prefix="/auth", tags=["Authentication"])

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# def generate_token(data: dict) -> str:
#     payload = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     payload.update({"exp": expire})
#     encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# @router.post("/login")
# def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     seller = db.query(models.Seller).filter(
#         models.Seller.username == request.username).first()
#     if not seller:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail="Username not found/ invalid user")

#     if not pwd_context.verify(request.password, seller.password):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="Invalid Password")
#     # Gen JWT Token
#     access_token = generate_token(data={"sub": seller.username})
#     return {"access_token": access_token, "token_type": "bearer"}


# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     # return username
