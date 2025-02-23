from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(AsyncAttrs, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String(312), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    rooms = relationship('Room', back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, created_at={self.created_at})>"
    
class Room(AsyncAttrs, Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    user = relationship('User', back_populates="rooms")
    messages = relationship('Message', back_populates='room')

    def __repr__(self):
        return f"<Room(roomid={self.id}, title={self.title}, created_at={self.created_at})>"
    
class Message(AsyncAttrs, Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    role = Column(Boolean, nullable=False)
    llm_id = Column(Integer, ForeignKey('llms.id'), nullable=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)
    web_search_flag = Column(Boolean, nullable=False)

    medias = relationship('Media', back_populates="message")
    room = relationship('Room', back_populates="messages")
    llm = relationship('Llm', back_populates="messages")
    medias = relationship('Media', back_populates="message")
    
    def __repr__(self):
        return f"<Message(message_id={self.id}, room_id={self.room_id}, user_or_llm_flag={self.role}, created_at={self.created_at})>"
    
class Llm(AsyncAttrs, Base):
    __tablename__ = 'llms'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    messages = relationship('Message', back_populates="llm")

    def __repr__(self):
        return f"<Llm(id={self.id}, email={self.name})>"
    
class Media(AsyncAttrs, Base):
    __tablename__ = 'medias'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    path = Column(String, index=True, nullable=False)
    type = Column(Integer,nullable=False )
    __table_args__ = (
        CheckConstraint('type BETWEEN 1 AND 3', name='check_type_between_1_and_3'),
    )
    text = Column(String, nullable=True)

    message = relationship('Message', back_populates="medias")

    def __repr__(self):
        return f"<Media(id={self.id}, url={self.path})>"
