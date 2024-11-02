from passlib.context import CryptContext


password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class HashPassword:
    @staticmethod
    def bcrypt(password: str):
        return password_context.hash(password)

    @staticmethod
    def verify(hashed_password, plain_password):
        return password_context.verify(plain_password, hashed_password)