from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    tablename = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    token = Column(String)
    billing_information = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum('user', 'admin'), default='user')
    organization_id = Column(Integer, nullable=True)

    subscription = relationship('Subscription', back_populates='users')
    documents = relationship('Document', back_populates='users')
    bot_instances = relationship('BotInstance', back_populates='users')
    usage_trackers = relationship('UsageTracker', back_populates='users')
    billing_records = relationship('Billing', back_populates='users')
    notifications = relationship('Notification', back_populates='users')
    organization_id = relationship('Organization', back_populates='users')
    
    def init(self, username, email, password):
        self.username = username
        self.email = email
        self.password = self.hash_password(password)

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def change_password(self, new_password):
        self.password = self.hash_password(new_password)

    def disable_enable_user(self, disable):
        if disable:
            self.is_active = False
        else:
            self.is_active = True

    def set_role(self, role):
        self.role = role
    
    def is_admin(self):
        return self.role == 'admin'

class Organization(Base):
    tablename = 'organization'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    
    users = relationship('User', back_populates='organization')


class Subscription(Base):
    tablename = 'subscription'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    max_uploads = Column(Integer, nullable=False)
    max_instances = Column(Integer, nullable=False)
    duration = Column(String, nullable=False)

    users = relationship('User', back_populates='subscription')
    
    

class Document(Base):
    tablename = 'documents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='pending')

    user = relationship('User', back_populates='documents')

class BotInstance(Base):
    tablename = 'bot_instances'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(Enum('Telegram', 'Website Component'), nullable=False)
    bot_token = Column(String)
    integration_token = Column(String)
    status = Column(String, default='active')

    user = relationship('User', back_populates='bot_instances')

class UsageTracker(Base):
    tablename = 'usage_trackers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bot_instance_id = Column(Integer, ForeignKey('bot_instances.id'), nullable=False)
    interaction_count = Column(Integer, default=0)
    upload_count = Column(Integer, default=0)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)

    user = relationship('User', back_populates='usage_trackers')
    bot_instance = relationship('BotInstance', back_populates='usage_trackers')

class Billing(Base):
    tablename = 'billing_records'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    amount = Column(Float, nullable=False)
    status = Column(Enum('Paid', 'Outstanding'), default='Outstanding')

    user = relationship('User', back_populates='billing_records')

class Notification(Base):
    tablename = 'notifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    type = Column(Enum('Outstanding Amount', 'Extra Usage'), nullable=False)

    user = relationship('User', back_populates='notifications')

class Admin(Base):
    tablename = 'admins'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    level = Column(Integer, nullable=False, default=0)
    
    def init(self, username, email, password, level):
        self.username = username
        self.email = email
        self.password = password
        self.level = level

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def change_password(self, new_password):
        self.password = self.hash_password(new_password)

    def disable_enable_user(self, disable):
        if disable:
            self.is_active = False
        else:
            self.is_active = True

    def set_level(self, level: int):
        self.level = level