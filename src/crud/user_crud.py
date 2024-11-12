from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.hash_password import HashPassword
from exceptions import UsernameAlreadyExistsException, EmailAlreadyExistsException
from models.users import User
from schemas.user_schema import UserCreate, UserUpdate


class UserCrud:
    @staticmethod
    async def get_users(session: AsyncSession):
        """Получение всех пользователей"""
        result = await session.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()
        return users

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int = None, email: str = None, username: str = None):
        """Получение конкретного пользователя по id, username или email"""
        if user_id:
            result = await session.execute(select(User).where(User.id == user_id, User.is_active == True))
        if email:
            result = await session.execute(select(User).where(User.email == email, User.is_active == True))
        if username:
            result = await session.execute(select(User).where(User.username == username, User.is_active == True))
        return result.scalars().first()

    @staticmethod
    async def create_user(session: AsyncSession, request: UserCreate):
        """Добавление пользователя"""
        username_exists = await session.execute(select(User).where(User.username == request.username))
        if username_exists.scalars().first():
            raise UsernameAlreadyExistsException(request.username)
        email_exists = await session.execute(select(User).where(User.email == request.email))
        if email_exists.scalars().first():
            raise EmailAlreadyExistsException(request.email)
        new_user = User()
        new_user.username = request.username
        new_user.email = request.email
        new_user.hashed_password = HashPassword.bcrypt(request.password)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def update_user(session: AsyncSession, request: UserUpdate, user_id: int):
        """Изменение данных о пользователе"""
        db_user = await UserCrud.get_user(session, user_id=user_id)
        if request.username:
            username_exists = await session.execute(select(User).where(
                User.username == request.username,
                            User.id != user_id
            ))
            if username_exists.scalars().first():
                raise UsernameAlreadyExistsException(request.username)
            db_user.username = request.username
        if request.email:
            email_exists = await session.execute(select(User).where(
                User.email == request.email,
                User.id != user_id
            ))
            if email_exists.scalars().first():
                raise EmailAlreadyExistsException(request.email)
            db_user.email = request.email
        if request.password:
            db_user.hashed_password = HashPassword.bcrypt(request.password)

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        return db_user

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int):
        """Удаление пользователя: изменение статуса активности"""
        db_user = await UserCrud.get_user(session, user_id=user_id)
        db_user.is_active = False
        session.add(db_user)
        await session.commit()
        return db_user
