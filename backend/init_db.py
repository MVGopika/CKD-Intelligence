"""
Database initialization script
Run this to set up the database with sample data
"""
from app.db.database import SessionLocal, init_db, engine
from app.db.models import Role, User
from app.core.security import hash_password
from datetime import datetime

def init_roles(db):
    """Initialize default roles"""
    roles = [
        {"name": "patient", "description": "Patient user"},
        {"name": "doctor", "description": "Doctor/Clinician"},
        {"name": "admin", "description": "Administrator"}
    ]
    
    for role_data in roles:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            print(f"Created role: {role_data['name']}")
    
    db.commit()

def create_demo_users(db):
    """Create demo users for testing"""
    # Get roles
    patient_role = db.query(Role).filter(Role.name == "patient").first()
    doctor_role = db.query(Role).filter(Role.name == "doctor").first()
    
    demo_users = [
        {
            "email": "patient@example.com",
            "full_name": "John Doe",
            "password": "patient123",
            "role_id": patient_role.id
        },
        {
            "email": "doctor@example.com",
            "full_name": "Dr. Sarah Smith",
            "password": "doctor123",
            "role_id": doctor_role.id
        }
    ]
    
    for user_data in demo_users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hash_password(user_data["password"]),
                role_id=user_data["role_id"],
                is_active=True
            )
            db.add(user)
            print(f"Created user: {user_data['email']}")
    
    db.commit()

def main():
    """Initialize database"""
    print("Initializing database...")
    
    # Create tables
    init_db()
    print("✓ Database tables created")
    
    # Get session
    db = SessionLocal()
    
    try:
        # Initialize roles
        init_roles(db)
        print("✓ Roles initialized")
        
        # Create demo users
        create_demo_users(db)
        print("✓ Demo users created")
        
        print("\n✅ Database initialization complete!")
        print("\nDemo Credentials:")
        print("  Patient: patient@example.com / patient123")
        print("  Doctor:  doctor@example.com / doctor123")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
