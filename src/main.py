import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from database import get_db
from models import Product, User

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
async def startup():
    from database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def get_user_from_session(request: Request):
    return request.session.get("user")

@app.get("/")
async def root(request: Request, db: AsyncSession = Depends(get_db)):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products, "user": user})

@app.get("/product/{product_id}")
async def get_product(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("product.html", {"request": request, "product": product, "user": user})

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user or not pwd_context.verify(password, user.hashed_password):
    # hashed_password = users.get(username)
    # if not hashed_password or not pwd_context.verify(password, hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные"})
    
    request.session["user"] = username
    return RedirectResponse(url="/", status_code=303)

@app.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# @app.post("/register")
# async def register(request: Request, username: str = Form(...), password: str = Form(...)):
#     try:
#         # Проверка на существующего пользователя
#         if username in users:
#             return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})
        
#         # Хешируем пароль и сохраняем пользователя
#         users[username] = pwd_context.hash(password)
        
#         # Перенаправляем на страницу входа после успешной регистрации
#         response = RedirectResponse(url="/login", status_code=303)
#         return response
    
#     except Exception as e:
#         # Отображаем отладочную информацию при возникновении ошибки
#         print(f"Ошибка регистрации: {e}")
#         return templates.TemplateResponse("register.html", {"request": request, "error": "Произошла ошибка при регистрации"})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    
    existing_user = await db.execute(select(User).where(User.username == username))
    if existing_user.scalars().first():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})
    
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/login")

@app.post("/add_product")
async def add_product(request: Request, name: str = Form(...), price: int = Form(...), db: AsyncSession = Depends(get_db)):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    
    new_product = Product(name=name, price=price)
    db.add(new_product)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_product")
async def delete_product(request: Request, product_id: int = Form(...), db: AsyncSession = Depends(get_db)):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        return RedirectResponse(url="/")
    
    await db.delete(product)
    await db.commit()
    return RedirectResponse(url="/", status_code=303)


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
    