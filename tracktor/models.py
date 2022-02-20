"""
Module for all models
"""
import uuid
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel.orm.session import Session
from werkzeug.security import generate_password_hash

from tracktor.error import ItemConflictException


class UserBase(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Base user model
    """

    name: str


class UserCreate(UserBase):  # pylint: disable=too-few-public-methods
    """
    Incoming model to create a user
    """

    password: str


class UserUpdate(UserBase):  # pylint: disable=too-few-public-methods
    """
    Incoming model to update a user
    """

    admin: bool


class UserResponse(UserUpdate):  # pylint: disable=too-few-public-methods
    """
    Cleaned user model suitable for a response
    """

    entity_id: str
    created_at: datetime
    last_login: Optional[datetime]


class User(UserResponse, UserCreate, table=True):
    """
    Full populated user model
    """

    id: int = Field(default=None, primary_key=True)
    entity_id: str = Field(default=str(uuid.uuid4()), nullable=False)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)

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
            check_user = (
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
    async def create(
        session: AsyncSession, name: str, password="", admin=False
    ) -> "User":
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

    @staticmethod
    async def get_all(session: AsyncSession) -> List["User"]:
        """
        Returns all existing users
        """
        return (await session.execute(select(User))).scalars().all()

    @staticmethod
    async def get_by_username(username: str, session: AsyncSession) -> Optional["User"]:
        """
        Returns a user with the given username
        """
        return (
            (await session.execute(select(User).where(User.name == username)))
            .scalars()
            .first()
        )

    @staticmethod
    async def get_by_entity_id(
        entity_id: str, session: AsyncSession
    ) -> Optional["User"]:
        """
        Returns a user with the given entity_id
        """
        return (
            (await session.execute(select(User).where(User.entity_id == entity_id)))
            .scalars()
            .first()
        )

    @staticmethod
    async def get_super_admin(session: AsyncSession):
        """
        Returns the admin user with id 1
        """
        return (
            (await session.execute(select(User).where(User.id == 1))).scalars().first()
        )


class BaseImage(SQLModel):
    """
    Base image model for playlists
    """

    entity_id: str


class PlaylistBase(SQLModel):
    """
    Base playlist model
    """

    entity_id: str
    name: str


class ItemBase(SQLModel):
    """
    Base item model
    """

    title: str
    artist: str


class CategoryBase(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Base category model
    """

    name: str


class Image(BaseImage, table=True):
    """
    Full populated image model
    """

    entity_id = Field(default=str(uuid.uuid4()), primary_key=True)
    image: str
    playlists: List["Playlist"] = Relationship(back_populates="image")


class CategoryResponse(CategoryBase):
    """
    Cleaned Category model for responses
    """

    playlists: List[PlaylistBase]

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.playlists = [PlaylistBase(**x.__dict__) for x in data.get("playlists")]


class Category(CategoryBase, table=True):
    """
    Full populated category model
    """

    id: int = Field(default=None, primary_key=True)
    playlists: List["Playlist"] = Relationship(back_populates="category")

    @staticmethod
    async def create(session: Session, name: str) -> "Category":
        """
        Creates a playlist item and saves it or returns an existing one
        """
        if (
            category := (
                await session.execute(select(Category).where(Category.name == name))
                if isinstance(session, AsyncSession)
                else session.execute(select(Category).where(Category.name == name))
            )
            .scalars()
            .first()
        ):
            return category
        category = Category(name=name)
        session.add(category)
        if isinstance(session, AsyncSession):
            await session.commit()
            await session.refresh(category)
        else:
            session.commit()
            session.refresh(category)
        return category

    @staticmethod
    async def get_all(session: Session) -> List["Category"]:
        """
        Returns all existing categories
        """
        return (
            (
                await session.execute(
                    select(Category).options(selectinload(Category.playlists))
                )
                if isinstance(session, AsyncSession)
                else session.execute(
                    select(Category).options(selectinload(Category.playlists))
                )
            )
            .scalars()
            .all()
        )

    @staticmethod
    async def get_by_name(name: str, session: AsyncSession) -> Optional["Category"]:
        """
        Returns a category with the given name
        """
        return (
            (
                await session.execute(
                    select(Category)
                    .where(Category.name == name)
                    .options(selectinload(Category.playlists))
                )
            )
            .scalars()
            .first()
        )


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


class ItemResponse(ItemBase):
    """
    Cleaned playlist item model suitable for a response
    """

    playlists: List[PlaylistBase]

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.playlists = [PlaylistBase(**x.__dict__) for x in data.get("playlists")]


class Item(ItemBase, table=True):
    """
    Full populated item model
    """

    id: int = Field(default=None, primary_key=True)
    playlists: List["Playlist"] = Relationship(
        back_populates="items", link_model=PlaylistItemLink
    )

    @staticmethod
    async def create(session: Session, title: str, artist: str) -> "Item":
        """
        Creates a playlist item and saves it or returns an existing one
        """
        if (
            item := (
                await session.execute(select(Item).where(Item.title == title))
                if isinstance(session, AsyncSession)
                else session.execute(select(Item).where(Item.title == title))
            )
            .scalars()
            .first()
        ):
            return item
        item = Item(title=title, artist=artist)
        session.add(item)
        if isinstance(session, AsyncSession):
            await session.commit()
            await session.refresh(item)
        else:
            session.commit()
            session.refresh(item)
        return item

    @staticmethod
    async def get_all(session: AsyncSession) -> List["Item"]:
        """
        Returns all existing items
        """
        return (
            (await session.execute(select(Item).options(selectinload(Item.playlists))))
            .scalars()
            .all()
        )


class PlaylistExtendedBase(PlaylistBase):
    """
    Cleaned playlist model suitable for a response
    """

    spotify: Optional[str]
    amazon: Optional[str]
    apple_music: Optional[str]
    image: Optional[BaseImage]
    release_date: Optional[datetime]


class PlaylistResponse(PlaylistExtendedBase):
    """
    Cleaned playlist model suitable for a response
    """

    items: List[ItemBase]
    category: Optional[CategoryBase]

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.image = (
            BaseImage(**data.get("image").__dict__) if data.get("image") else None
        )


class Playlist(PlaylistExtendedBase, table=True):
    """
    Full populated playlist model
    """

    id: int = Field(default=None, primary_key=True)
    entity_id: str = Field(default=str(uuid.uuid4()), nullable=False)
    items: List[Item] = Relationship(
        back_populates="playlists", link_model=PlaylistItemLink
    )
    category: Optional[Category] = Relationship(back_populates="playlists")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    image: Optional[Image] = Relationship(back_populates="playlists")
    image_id: Optional[uuid.UUID] = Field(default=None, foreign_key="image.entity_id")

    @staticmethod
    async def create(  # pylint: disable=too-many-arguments
        session: Session,
        name: str,
        spotify: Optional[str] = None,
        amazon: Optional[str] = None,
        apple_music: Optional[str] = None,
        items: List[ItemResponse] = None,
        image: Optional[Image] = None,
        category: Optional[Category] = None,
        release_date: Optional[datetime] = None,
    ) -> "Playlist":
        """
        Creates a playlist and saves it
        """
        playlist = (
            (
                await session.execute(select(Playlist).where(Playlist.name == name))
                if isinstance(session, AsyncSession)
                else session.execute(select(Playlist).where(Playlist.name == name))
            )
            .scalars()
            .first()
        )
        if not playlist:
            playlist = Playlist(
                name=name, spotify=spotify, amazon=amazon, apple_music=apple_music
            )
            session.add(playlist)
            if isinstance(session, AsyncSession):
                await session.commit()
                await session.refresh(playlist)
            else:
                session.commit()
                session.refresh(playlist)
        playlist.items = [await Item.create(session, **x.__dict__) for x in items]
        playlist.category_id = category.id if category else None
        playlist.image_id = image.entity_id if image else None
        playlist.release_date = release_date if release_date else None

        session.add(playlist)
        if isinstance(session, AsyncSession):
            await session.commit()
            await session.refresh(playlist)
        else:
            session.commit()
            session.refresh(playlist)
        return playlist

    @staticmethod
    async def get_all(session: Session) -> List["Playlist"]:
        """
        Returns all existing playlists
        """
        return (
            (
                await session.execute(
                    select(Playlist).options(
                        selectinload(Playlist.items),
                        selectinload(Playlist.category),
                        selectinload(Playlist.image),
                    )
                )
                if isinstance(session, AsyncSession)
                else session.execute(
                    select(Playlist).options(
                        selectinload(Playlist.items),
                        selectinload(Playlist.category),
                        selectinload(Playlist.image),
                    )
                )
            )
            .scalars()
            .all()
        )

    @staticmethod
    async def get_by_entity_id(
        entity_id: str, session: AsyncSession
    ) -> Optional["Playlist"]:
        """
        Returns a playlist with the given entity_id
        """
        return (
            (
                await session.execute(
                    select(Playlist)
                    .where(Playlist.entity_id == entity_id)
                    .options(
                        selectinload(Playlist.items),
                        selectinload(Playlist.category),
                        selectinload(Playlist.image),
                    )
                )
            )
            .scalars()
            .first()
        )
