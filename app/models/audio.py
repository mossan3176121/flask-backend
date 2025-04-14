from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, Float

Base = declarative_base()

class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True)
    verb = Column(Text, nullable=False)
    verb_jp = Column(Text, nullable=False)
    sentence = Column(Text, nullable=False)
    sentence_jp = Column(Text, nullable=False)
    path = Column(Text, nullable=False)

class MiniConversationFile(Base):
    __tablename__ = "mini_conversation"
    id = Column(Integer, primary_key=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    speaker = Column(Text, nullable=False)
    sentence = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
