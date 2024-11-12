from passlib.context import CryptContext


password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class HashPassword:
    @staticmethod
    def bcrypt(password: str):
        """Хэширование пароля"""
        return password_context.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str):
        """Проверка валидности пароля"""
        return password_context.verify(plain_password, hashed_password)