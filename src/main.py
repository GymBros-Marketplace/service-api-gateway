import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

products = [
    {"id": 1, "name": "Футболка", "price": 500},
    {"id": 2, "name": "Куртка", "price": 2000},
    {"id": 3, "name": "Штаны", "price": 1200},
    {"id": 4, "name": "Кроссовки", "price": 3000},
    {"id": 5, "name": "Свитер", "price": 1500}
]

users = {}

def generate_product_id():
    return max([product["id"] for product in products]) + 1 if products else 1

def get_user_from_session(request: Request):
    return request.session.get("user")

@app.get("/")
async def root(request: Request):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "products": products, "user": user})

@app.get("/product/{product_id}")
async def get_product(request: Request, product_id: int):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    
    product = next((product for product in products if product["id"] == product_id), None)
    if product is None:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("product.html", {"request": request, "product": product, "user": user})

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    hashed_password = users.get(username)
    if not hashed_password or not pwd_context.verify(password, hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные"})
    request.session["user"] = username
    return RedirectResponse(url="/", status_code=303)

@app.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        # Проверка на существующего пользователя
        if username in users:
            return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})
        
        # Хешируем пароль и сохраняем пользователя
        users[username] = pwd_context.hash(password)
        
        # Перенаправляем на страницу входа после успешной регистрации
        response = RedirectResponse(url="/login", status_code=303)
        return response
    
    except Exception as e:
        # Отображаем отладочную информацию при возникновении ошибки
        print(f"Ошибка регистрации: {e}")
        return templates.TemplateResponse("register.html", {"request": request, "error": "Произошла ошибка при регистрации"})

@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/login")

@app.post("/add_product")
async def add_product(request: Request, name: str = Form(...), price: int = Form(...)):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    
    new_product = {"id": generate_product_id(), "name": name, "price": price}
    products.append(new_product)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_product")
async def delete_product(request: Request, product_id: int = Form(...)):
    user = get_user_from_session(request)
    if user is None:
        return RedirectResponse(url="/login")
    
    global products
    products = [product for product in products if product["id"] != product_id]
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    