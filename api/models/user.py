from datetime import datetime
from typing import Optional
from odmantic import Model
from enum import Enum


class Role(str, Enum):
    default = "default"
    support = "support"
    admin = "admin"


class AuthUser(Model):
    username: str
    email: str
    # Note: first name and last name are NOT always the same as for the User class!
    # AuthUser = User info from IDP (Authentication server / Identity Provider) = real names
    # User = User info from API database (info used in the app) = names to use for pdf export
    first_name: Optional[str]
    last_name: Optional[str]
    locale: Optional[str]
    roles: list[Role] = [Role.default]

    def __str__(self) -> str:
        return f"{self.username} / {self.first_name} {self.last_name} / {self.roles} / {self.email} / {self.locale}"


class User(Model):
    username: str
    email: str
    roles: list[Role] = [Role.default]
    # Note: first name and last name are NOT always the same as for the Auth0 class!
    # AuthUser = User info from IDP (Authentication server / Identity Provider) = real names
    # User = User info from API database (info used in the app) = names to use for pdf export
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    locale: Optional[str]
    model_config = {
        "collection": "users"
    }

    def __str__(self) -> str:
        return f"{self.username} / {self.title} {self.first_name} {self.last_name} / {self.email} / {self.locale}"
