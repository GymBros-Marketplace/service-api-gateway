from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from models import User  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_default_user(db: AsyncSession):
    result = await db.execute(select(User).where(User.username == "admin"))
    user = result.scalars().first()

    if user is None:
        hashed_password = pwd_context.hash("admin")
        
        new_user = User(username="admin", hashed_password=hashed_password, is_admin = True)
        print(new_user.id)
        db.add(new_user)
        await db.commit()
