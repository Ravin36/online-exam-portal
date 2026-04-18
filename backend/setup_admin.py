#!/usr/bin/env python3
"""
Script to setup admin user credentials in the database
Username: admin
Password: admin@123
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Password hashing setup
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def _normalize_password(password):
    if isinstance(password, str):
        password = password.encode("utf-8")
    if len(password) > 72:
        return password[:72]
    return password

def get_password_hash(password):
    """Hash password"""
    return pwd_context.hash(_normalize_password(password))

def setup_admin():
    """Setup or update admin user"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'exam_portal')
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Admin credentials
            admin_username = "admin"
            admin_password = "admin@123"
            admin_email = "admin@examportal.com"
            admin_full_name = "System Administrator"
            
            # Hash the password
            hashed_password = get_password_hash(admin_password)
            
            # Check if admin user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (admin_username,))
            existing_admin = cursor.fetchone()
            
            if existing_admin:
                # Update existing admin user
                cursor.execute(
                    """UPDATE users SET password = %s, email = %s, full_name = %s, role = 'admin' 
                       WHERE username = %s""",
                    (hashed_password, admin_email, admin_full_name, admin_username)
                )
                connection.commit()
                print("✅ Admin user updated successfully!")
                print(f"   Username: {admin_username}")
                print(f"   Password: {admin_password}")
            else:
                # Insert new admin user
                cursor.execute(
                    """INSERT INTO users (username, email, password, role, full_name) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (admin_username, admin_email, hashed_password, 'admin', admin_full_name)
                )
                connection.commit()
                print("✅ Admin user created successfully!")
                print(f"   Username: {admin_username}")
                print(f"   Password: {admin_password}")
                print(f"   User ID: {cursor.lastrowid}")
            
            cursor.close()
    
    except Error as e:
        print(f"❌ Database error: {e}")
        print(f"   DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
        print(f"   DB_USER: {os.getenv('DB_USER', 'root')}")
        print(f"   DB_NAME: {os.getenv('DB_NAME', 'exam_portal')}")
        print("\n   Please check your .env file and ensure MySQL is running.")
        return False
    
    finally:
        if connection and connection.is_connected():
            connection.close()
    
    return True

if __name__ == "__main__":
    print("🔧 Setting up admin credentials...")
    print("-" * 40)
    setup_admin()
