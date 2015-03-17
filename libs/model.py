from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(String(64), primary_key=True)
    layer = Column(String(120), primary_key=True)
    tag = Column(String(120),  primary_key=True)

    def __repr__(self):
        return '<Tag layer=%r tag=%r id=%r>' % (self.layer, self.tag, self.id)

class Image(Base):
    __tablename__ = 'image'
    id = Column(String(64), primary_key=True)
    parent = Column(String(64), index=True)
    author = Column(String(256))
    layer = Column(String(120), index=True)
    tag = Column(String(120), index=True)

    def __repr__(self):
        return '<Image layer=%r author=%r id=%r parent=%r>' % (self.layer, self.tag, self.id, self.parent)
 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
print "done"
