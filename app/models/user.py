"""
Modelo User — Tabla 1 (Documento 07 — Diseño de Base de Datos).

Representa cada usuario registrado en Together.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.personal_category import PersonalCategory
    from app.models.personal_expense import PersonalExpense
    from app.models.personal_income import PersonalIncome
    from app.models.session import Session
    from app.models.user_settings import UserSettings


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    language: Mapped[str] = mapped_column(String(5), nullable=False, default="es")
    currency: Mapped[str] = mapped_column(String(5), nullable=False, default="COP")
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="America/Bogota"
    )

    # OAuth (Google / Apple)
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    apple_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Control de intentos fallidos de login (bloqueo tras 5 intentos — Doc 12)
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    personal_categories: Mapped[list["PersonalCategory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    personal_expenses: Mapped[list["PersonalExpense"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    personal_incomes: Mapped[list["PersonalIncome"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
