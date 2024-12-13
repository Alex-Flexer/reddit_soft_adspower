from typing import Optional, List
from datetime import date

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import create_engine, ForeignKey

engine = create_engine("sqlite:///database/database.db")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str]

    user_password: Mapped[str]

    authorization_code: Mapped[Optional[str]]

    confirmed_status: Mapped[bool]

    current_price: Mapped[Optional[float]]

    active_subscription_price: Mapped[Optional[int]]

    subscription_end_date: Mapped[Optional[date]]

    telegram_id: Mapped[Optional[int]]

    token: Mapped[Optional[str]]

    reddit_accounts: Mapped[List["RedditAccount"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return f"{self.id} {self.email} {self.user_password} {self.subscription_end_date}"

    def __repr__(self) -> str:
        return f"{self.id} {self.email} {self.user_password} {self.subscription_end_date}"


class RedditAccount(Base):
    __tablename__ = "reddit_accounts_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner: Mapped["User"] = relationship(back_populates="reddit_accounts")

    owner_id: Mapped[int] = mapped_column(ForeignKey("users_table.id"))

    email: Mapped[Optional[str]]

    password: Mapped[Optional[str]]

    proxy_host: Mapped[str]

    proxy_port: Mapped[int]

    proxy_user: Mapped[str]

    proxy_password: Mapped[str]

    def __str__(self) -> str:
        return f"{self.id} {self.email} {self.password} {self.owner.email}"

    def __repr__(self) -> str:
        return f"{self.id} {self.email} {self.password} {self.owner.email}"


Base.metadata.create_all(engine)
