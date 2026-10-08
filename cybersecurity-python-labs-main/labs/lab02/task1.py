import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, Set

# Константи
ITERATIONS = 100_000
SESSION_TIMEOUT_SEC = 900
EMAIL_REGEX = r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class User:
    def __init__(self, username: str, email: str, role: str, active: bool = True):
        self.username = username
        self.email = email
        self.role = role
        self.active = active
        self.__password_hash: Optional[bytes] = None
        self.__password_salt: Optional[bytes] = None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid email format")
        self._email = value

    def set_password(self, password: str):
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), self.__password_salt, ITERATIONS
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_hash or not self.__password_salt:
            return False
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), self.__password_salt, ITERATIONS
        )
        return hmac.compare_digest(self.__password_hash, new_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        return f"User({self.username}, {self.email}, role={self.role}, active={self.active})"


class Admin(User):
    def __init__(self, username: str, email: str, permissions: Set[str] = None):
        super().__init__(username, email, role="admin")
        self.permissions = permissions if permissions is not None else set()

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self):
        return f"{super().__str__()}, permissions={self.permissions}"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        self.login_time = datetime.now(timezone.utc)
        self.last_activity = self.login_time

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec < 0:
            raise ValueError("Timeout cannot be negative")
        return (datetime.now(timezone.utc) - self.last_activity) < timedelta(seconds=timeout_sec)


@dataclass
class LogEntry:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.logs: list[LogEntry] = []

    def add_log(self, username: str, action: str):
        self.logs.append(LogEntry(datetime.now(timezone.utc), username, action))

    def show_all(self):
        for log in self.logs:
            print(f"{log.timestamp} | {log.username} | {log.action}")


class UserAccount:
    def __init__(self, user: User, session: Session = None, audit: AuditLog = None):
        self.user = user
        self.session = session
        self.audit = audit or AuditLog()

    def login(self, username: str, password: str, ip: str):
        if self.user.username == username and self.user.check_password(password):
            self.session = Session(ip)
            self.audit.add_log(username, "login_success")
        else:
            self.audit.add_log(username, "login_failure")

    def is_authenticated(self) -> bool:
        return self.session is not None and self.session.is_active(SESSION_TIMEOUT_SEC)

    def logout(self):
        self.session = None
        self.audit.add_log(self.user.username, "logout")

    def __getitem__(self, key):
        if key in ["user", "session", "audit"]:
            return getattr(self, key)
        raise KeyError(f"Key {key} not allowed")

    def __setitem__(self, key, value):
        if key in ["user", "session"]:
            if not isinstance(value, (User, Session)):
                raise TypeError("Invalid type")
            setattr(self, key, value)
        else:
            raise KeyError("Key not allowed or read-only")