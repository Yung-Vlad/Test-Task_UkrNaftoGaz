import re
from zxcvbn import zxcvbn


class Validator:
    @staticmethod
    def check_password_complexity(password: str) -> str | None:
        if len(password) < 8:  # Length
            return "Password is too short!"
        elif not bool(re.search(r'\d', password)):  # Exists numbers
            return "Password must contain number(s)!"
        elif not bool(re.search(r"[A-Za-z]", password)):  # Exists letters
            return "Password must contain letter(s)!"
        elif zxcvbn(password)["score"] < 2:  # Password strength
            return "Password is too easy!"

        return None

    @staticmethod
    def check_valid_email(email: str) -> bool:
        pattern: str = r"^[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return bool(re.match(pattern, email))
