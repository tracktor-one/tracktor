"""
Module for all models
"""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import SQLModel, Field, Relationship
from werkzeug.security import generate_password_hash

from tracktor.error import ItemConflictException


class UserCreate(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Incoming model to create a user
    """

    name: str
    password: str


class UserUpdate(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Incoming model to update a user
    """

    name: str
    admin: bool


class UserResponse(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Cleaned user model suitable for a response
    """

    entity_id: str
    name: str
    created_at: datetime
    last_login: Optional[datetime]
    admin: bool


class User(UserResponse, table=True):
    """
    Full populated user model
    """

    id: int = Field(default=None, primary_key=True)
    entity_id: str = Field(default=str(uuid.uuid1()), nullable=False)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    password: str

    async def update(  # pylint: disable=too-many-arguments
        self,
        session: AsyncSession,
        name: Optional[str] = None,
        password: Optional[str] = None,
        last_login: Optional[datetime] = None,
        admin: Optional[bool] = None,
    ):
        """
        Updates the values of a user in the database
        """
        changed = False
        if name:
            check_user: User = (
                (await session.execute(select(User).where(User.name == name)))
                .scalars()
                .first()
            )
            if check_user and check_user.id != self.id:
                raise ItemConflictException(message="Invalid username")
            self.name = name
            changed = True
        if password:
            self.password = generate_password_hash(password)
            changed = True
        if last_login:
            self.last_login = last_login
            changed = True
        if admin is not None:
            self.admin = admin
            changed = True

        if changed:
            session.add(self)
            await session.commit()
            await session.refresh(self)

        return self

    async def delete(self, session: AsyncSession):
        """
        Removes a user from the database
        """
        await session.delete(self)
        await session.commit()

    @staticmethod
    async def create(session: AsyncSession, name: str, password="", admin=False):
        """
        Creates a new user and saves it to the database
        """
        user = User(
            name=name,
            password=generate_password_hash(password) if password else None,
            admin=admin,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


class CategoryResponse(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Cleaned category model suitable for a response
    """

    name: str
    playlists: List["Playlist"] = Relationship(back_populates="category")


class Category(CategoryResponse, table=True):
    """
    Full populated category model
    """

    id: int = Field(default=None, primary_key=True)

    @staticmethod
    async def create(session: AsyncSession, name: str):
        """
        Creates a playlist item and saves it or returns an existing one
        """
        if (
            category := (
                await session.execute(select(Category).where(Category.name == name))
            )
            .scalars()
            .first()
        ):
            return category
        category = Category(name=name)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category


class VersionModel(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Version response model
    """

    version: str
    changelog: str


class Token(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Token response model
    """

    access_token: str
    token_type: str


class PlaylistItemLink(SQLModel, table=True):
    """
    Many-to-Many Table for Playlist and Items
    """

    playlist_id: Optional[int] = Field(
        default=None, foreign_key="playlist.id", primary_key=True
    )
    item_id: Optional[int] = Field(
        default=None, foreign_key="item.id", primary_key=True
    )


class ItemResponse(SQLModel):
    """
    Cleaned playlist item model suitable for a response
    """

    title: str
    artist: str


class Item(ItemResponse, table=True):
    """
    Full populated item model
    """

    id: int = Field(default=None, primary_key=True)
    playlists: List["Playlist"] = Relationship(
        back_populates="items", link_model=PlaylistItemLink
    )

    @staticmethod
    async def create(session: AsyncSession, title: str, artist: str):
        """
        Creates a playlist item and saves it or returns an existing one
        """
        if (
            item := (
                await session.execute(
                    select(Item).where(Item.title == title, Item.artist == artist)
                )
            )
            .scalars()
            .first()
        ):
            return item
        item = Item(title=title, artist=artist)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


class PlaylistResponse(SQLModel):
    """
    Cleaned playlist model suitable for a response
    """

    entity_id: str
    name: str
    spotify: Optional[str]
    amazon: Optional[str]
    apple_music: Optional[str]
    items: List[ItemResponse]
    image: Optional[str] = None
    category: Optional[Category] = Relationship(back_populates="playlists")
    release_date: Optional[datetime]


class Playlist(PlaylistResponse, table=True):
    """
    Full populated playlist model
    """

    id: int = Field(default=None, primary_key=True)
    items: List[Item] = Relationship(
        back_populates="playlists", link_model=PlaylistItemLink
    )
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    @staticmethod
    async def create(  # pylint: disable=too-many-arguments
        session: AsyncSession,
        name: str,
        spotify: Optional[str] = None,
        amazon: Optional[str] = None,
        apple_music: Optional[str] = None,
        items: List[ItemResponse] = None,
        image: Optional[str] = None,
        category: Optional[Category] = None,
        release_date: Optional[datetime] = None,
    ):
        """
        Creates a playlist and saves it
        """
        playlist = Playlist(
            name=name,
            spotify=spotify,
            amazon=amazon,
            apple_music=apple_music,
            image=image,
            release_date=release_date,
        )
        session.add(playlist)
        await session.commit()
        await session.refresh(playlist)
        playlist.items = [Item.create(session, **x.__dict__) for x in items]
        if category:
            playlist.category = category

        session.add(playlist)
        await session.commit()
        await session.refresh(playlist)
        return playlist
