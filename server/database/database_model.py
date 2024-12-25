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

    active_subscription_price: Mapped[Optional[int]]

    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    token: Mapped[Optional[str]]

    def __str__(self) -> str:
        return f"{self.id} {self.email}"

    def __repr__(self) -> str:
        return str(self)


class RedditAccount(Base):
    __tablename__ = "reddit_accounts_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    subscription: Mapped["Subscription"] = relationship(back_populates="reddit_accounts")

    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions_table.id"))

    ads_id: Mapped[str]

    def __str__(self) -> str:
        return f"{self.id} {self.ads_id}"

    def __repr__(self) -> str:
        return str(self)


class Subscription(Base):
    __tablename__ = "subscriptions_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner: Mapped["User"] = relationship(back_populates="subscriptions")

    owner_id: Mapped[int] = mapped_column(ForeignKey("users_table.id"))

    end_date: Mapped[date]

    amount_accounts_limit: Mapped[int]

    reddit_accounts: Mapped[List["RedditAccount"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return f"{self.id} {self.owner.email} {self.end_date} {self.amount_accounts_limit}"

    def __repr__(self) -> str:
        return str(self)

Base.metadata.create_all(engine)
