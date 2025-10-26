from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, UniqueConstraint, CheckConstraint, JSON,
    create_engine, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import db_config

# Create the base class for our models
Base = declarative_base()

class ModelType(Base):
    __tablename__ = 'model_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('model_types.id', ondelete='SET NULL'))
    type_kind = Column(Text, nullable=False)
    is_action = Column(Boolean, default=False)
    description = Column(Text)
    
    # Relationships
    parent = relationship("ModelType", remote_side=[id])
    children = relationship("ModelType", back_populates="parent")
    models = relationship("Model", back_populates="model_type")
    attribute_definitions = relationship("AttributeDefinition", back_populates="model_type")
    trait_assignments = relationship("TraitAssignment", back_populates="trait_type")
    
    __table_args__ = (
        CheckConstraint("type_kind IN ('base', 'trait')", name='check_type_kind'),
    )
    
    def __repr__(self):
        return f"<ModelType(id={self.id}, name='{self.name}', type_kind='{self.type_kind}')>"

class Model(Base):
    __tablename__ = 'models'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_type_id = Column(Integer, ForeignKey('model_types.id', ondelete='CASCADE'), nullable=False)
    title = Column(Text, nullable=False)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model_type = relationship("ModelType", back_populates="models")
    trait_assignments = relationship("TraitAssignment", back_populates="model")
    attributes = relationship("Attribute", back_populates="model")
    from_relations = relationship("Relation", foreign_keys="Relation.from_id", back_populates="from_model")
    to_relations = relationship("Relation", foreign_keys="Relation.to_id", back_populates="to_model")
    embedding = relationship("Embedding", back_populates="model", uselist=False)
    
    def __repr__(self):
        return f"<Model(id={self.id}, title='{self.title}', type_id={self.model_type_id})>"

class TraitAssignment(Base):
    __tablename__ = 'trait_assignments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'), nullable=False)
    trait_type_id = Column(Integer, ForeignKey('model_types.id', ondelete='CASCADE'), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model = relationship("Model", back_populates="trait_assignments")
    trait_type = relationship("ModelType", back_populates="trait_assignments")
    
    __table_args__ = (
        UniqueConstraint('model_id', 'trait_type_id', name='unique_trait_assignment'),
    )
    
    def __repr__(self):
        return f"<TraitAssignment(model_id={self.model_id}, trait_type_id={self.trait_type_id})>"

class AttributeDefinition(Base):
    __tablename__ = 'attribute_definitions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_type_id = Column(Integer, ForeignKey('model_types.id', ondelete='CASCADE'), nullable=False)
    key = Column(Text, nullable=False)
    value_type = Column(Text, nullable=False)
    required = Column(Boolean, default=False)
    constraints = Column(JSON, default={})
    
    # Relationships
    model_type = relationship("ModelType", back_populates="attribute_definitions")
    attributes = relationship("Attribute", back_populates="attribute_definition")
    
    __table_args__ = (
        UniqueConstraint('model_type_id', 'key', name='unique_attribute_definition'),
        CheckConstraint("value_type IN ('string', 'number', 'datetime', 'boolean', 'vector')", name='check_value_type'),
    )
    
    def __repr__(self):
        return f"<AttributeDefinition(id={self.id}, key='{self.key}', value_type='{self.value_type}')>"

class Attribute(Base):
    __tablename__ = 'attributes'
    
    id = Column(BigInteger, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'), nullable=False)
    attribute_definition_id = Column(Integer, ForeignKey('attribute_definitions.id', ondelete='CASCADE'), nullable=False)
    value_text = Column(Text)
    value_number = Column(Integer)  # Using Integer instead of double precision for simplicity
    value_time = Column(DateTime)
    value_bool = Column(Boolean)
    # Note: vector type would need pgvector extension - using Text for now
    value_vector = Column(Text)  # Will store as text representation
    
    # Relationships
    model = relationship("Model", back_populates="attributes")
    attribute_definition = relationship("AttributeDefinition", back_populates="attributes")
    
    __table_args__ = (
        UniqueConstraint('model_id', 'attribute_definition_id', 'value_text', 'value_number', 'value_time', 'value_bool', name='unique_attribute_value'),
    )
    
    def __repr__(self):
        return f"<Attribute(id={self.id}, model_id={self.model_id}, key='{self.attribute_definition.key if self.attribute_definition else 'N/A'}')>"

class RelationshipType(Base):
    __tablename__ = 'relationship_type'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_model_type_id = Column(Integer, ForeignKey('model_types.id', ondelete='CASCADE'), nullable=False)
    to_model_type_id = Column(Integer, ForeignKey('model_types.id', ondelete='CASCADE'), nullable=False)
    relation_name = Column(Text, nullable=False)
    multiplicity = Column(Text, default='many')
    description = Column(Text)
    
    # Relationships
    from_model_type = relationship("ModelType", foreign_keys=[from_model_type_id])
    to_model_type = relationship("ModelType", foreign_keys=[to_model_type_id])
    relations = relationship("Relation", back_populates="relationship_type")
    relation_attribute_definitions = relationship("RelationAttributeDefinition", back_populates="relationship_type")
    
    __table_args__ = (
        UniqueConstraint('from_model_type_id', 'to_model_type_id', 'relation_name', name='unique_relationship_type'),
    )
    
    def __repr__(self):
        return f"<RelationshipType(id={self.id}, relation_name='{self.relation_name}')>"

class RelationAttributeDefinition(Base):
    __tablename__ = 'relation_attribute_definitions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    relationship_type_id = Column(Integer, ForeignKey('relationship_type.id', ondelete='CASCADE'), nullable=False)
    key = Column(Text, nullable=False)
    value_type = Column(Text, nullable=False)
    required = Column(Boolean, default=False)
    
    # Relationships
    relationship_type = relationship("RelationshipType", back_populates="relation_attribute_definitions")
    relation_attributes = relationship("RelationAttribute", back_populates="relation_attribute_definition")
    
    __table_args__ = (
        UniqueConstraint('relationship_type_id', 'key', name='unique_relation_attribute_definition'),
        CheckConstraint("value_type IN ('string', 'number', 'datetime', 'boolean', 'vector')", name='check_relation_value_type'),
    )
    
    def __repr__(self):
        return f"<RelationAttributeDefinition(id={self.id}, key='{self.key}', value_type='{self.value_type}')>"

class Relation(Base):
    __tablename__ = 'relations'
    
    id = Column(BigInteger, primary_key=True)
    from_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'), nullable=False)
    to_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'), nullable=False)
    relationship_type_id = Column(Integer, ForeignKey('relationship_type.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    from_model = relationship("Model", foreign_keys=[from_id], back_populates="from_relations")
    to_model = relationship("Model", foreign_keys=[to_id], back_populates="to_relations")
    relationship_type = relationship("RelationshipType", back_populates="relations")
    relation_attributes = relationship("RelationAttribute", back_populates="relation")
    
    def __repr__(self):
        return f"<Relation(id={self.id}, from_id={self.from_id}, to_id={self.to_id})>"

class RelationAttribute(Base):
    __tablename__ = 'relation_attributes'
    
    id = Column(BigInteger, primary_key=True)
    relation_id = Column(BigInteger, ForeignKey('relations.id', ondelete='CASCADE'), nullable=False)
    relation_attribute_definition_id = Column(Integer, ForeignKey('relation_attribute_definitions.id', ondelete='CASCADE'), nullable=False)
    value_text = Column(Text)
    value_number = Column(Integer)
    value_time = Column(DateTime)
    value_bool = Column(Boolean)
    value_vector = Column(Text)  # Will store as text representation
    
    # Relationships
    relation = relationship("Relation", back_populates="relation_attributes")
    relation_attribute_definition = relationship("RelationAttributeDefinition", back_populates="relation_attributes")
    
    __table_args__ = (
        UniqueConstraint('relation_id', 'relation_attribute_definition_id', 'value_text', 'value_number', 'value_time', 'value_bool', name='unique_relation_attribute_value'),
    )
    
    def __repr__(self):
        return f"<RelationAttribute(id={self.id}, relation_id={self.relation_id})>"

class Embedding(Base):
    __tablename__ = 'embeddings'
    
    model_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'), primary_key=True)
    embedding = Column(Text)  # Will store vector as text representation
    
    # Relationships
    model = relationship("Model", back_populates="embedding")
    
    def __repr__(self):
        return f"<Embedding(model_id={self.model_id})>"

# Create engine
engine = create_engine(db_config.database_url, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
