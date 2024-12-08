# coding: utf-8
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship



from app.database import Base


class MedicineType(Base):
    __tablename__ = "medicine_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String(150), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    size_id = Column(Integer, ForeignKey("medicine_size_codes.id"), nullable=False)
    x = Column(Integer, nullable=False)  # Position X
    y = Column(Integer, nullable=False)  # Position Y

    size = relationship("MedicineSizeCode", backref="medicine_types")
    instances = relationship("MedicineInstance", back_populates="medicine_type", cascade="all, delete")


class MedicineInstance(Base):
    __tablename__ = "medicine_instances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_type_id = Column(Integer, ForeignKey("medicine_types.id", ondelete="CASCADE"), nullable=False)
    batch_number = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    expiration_date = Column(Date, nullable=False)

    medicine_type = relationship("MedicineType", back_populates="instances")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)  # Changed from 'name'
    last_name = Column(String(100), nullable=False)   # New column
    identity_number = Column(String(20), unique=True, nullable=False)  # New column
    age = Column(Integer, nullable=False)
    gender_id = Column(Integer, ForeignKey("gender_codes.id"), nullable=False)
    contact_info = Column(String(150))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    gender = relationship("GenderCode", backref="patients")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)  # Renamed from 'name'
    first_name = Column(String(100), nullable=False)  # New column
    last_name = Column(String(100), nullable=False)   # New column
    identity_number = Column(String(20), unique=True, nullable=False)  # New column
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("role_codes.id"), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    role = relationship("RoleCode", backref="users")

class Action(Base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('actions_id_seq'::regclass)"))
    action_type = Column(String(100), nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='SET NULL'))
    details = Column(JSONB(astext_type=Text()))
    action_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_type_id = Column(Integer, ForeignKey("medicine_types.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    medicine_type = relationship("MedicineType")



class Prescription(Base):
    __tablename__ = 'prescriptions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('prescriptions_id_seq'::regclass)"))
    patient_id = Column(ForeignKey('patients.id', ondelete='CASCADE'))
    prescribed_by = Column(ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    patient = relationship('Patient')
    user = relationship('User')
    # Relationship to PrescriptionItem
    prescription_items = relationship("PrescriptionItem", back_populates="prescription")

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"))
    medicine_id = Column(Integer, ForeignKey("medicine_types.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False)

    medicine_type = relationship("MedicineType")
# Relationship back to Prescription
    prescription = relationship("Prescription", back_populates="prescription_items")

    # Relationship to MedicineType
    medicine = relationship("MedicineType", backref="prescription_items")
class GenderCode(Base):
    __tablename__ = 'gender_codes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

class MedicineSizeCode(Base):
    __tablename__ = 'medicine_size_codes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

class RoleCode(Base):
    __tablename__ = 'role_codes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)