#!/usr/bin/env python3
"""
Diagnostic script to check MySQL connection and database status
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def check_mysql_status():
    """Check MySQL connection and database status"""
    
    print("=" * 60)
    print("MySQL Diagnostic Check")
    print("=" * 60)
    
    # Show configuration
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'exam_portal')
    
    print(f"\nConfiguration from .env:")
    print(f"  DB_HOST: {db_host}")
    print(f"  DB_USER: {db_user}")
    print(f"  DB_PASSWORD: {'*' * len(db_password) if db_password else '(empty)'}")
    print(f"  DB_NAME: {db_name}")
    
    # Try to connect to MySQL server
    print("\n1. Attempting to connect to MySQL server...")
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        
        if connection.is_connected():
            print("   ✅ MySQL server connection successful!")
            
            cursor = connection.cursor()
            
            # Check if database exists
            print(f"\n2. Checking if database '{db_name}' exists...")
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            db_exists = cursor.fetchone()
            
            if db_exists:
                print(f"   ✅ Database '{db_name}' found!")
                
                # Switch to database
                cursor.execute(f"USE {db_name}")
                
                # Check if users table exists
                print(f"\n3. Checking if 'users' table exists...")
                cursor.execute("SHOW TABLES LIKE 'users'")
                table_exists = cursor.fetchone()
                
                if table_exists:
                    print("   ✅ Table 'users' found!")
                    
                    # Check admin user
                    print(f"\n4. Checking for admin user...")
                    cursor.execute("SELECT id, username, email, role FROM users WHERE username = 'admin'")
                    admin = cursor.fetchone()
                    
                    if admin:
                        print(f"   ✅ Admin user found!")
                        print(f"      ID: {admin[0]}")
                        print(f"      Username: {admin[1]}")
                        print(f"      Email: {admin[2]}")
                        print(f"      Role: {admin[3]}")
                        print(f"\n   ⚠️  To update the password, run the setup script or use the SQL command in SETUP_ADMIN_CREDENTIALS.md")
                    else:
                        print(f"   ❌ Admin user NOT found!")
                        print(f"      Run the setup script or use the SQL command in SETUP_ADMIN_CREDENTIALS.md")
                    
                    # Count total users
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    print(f"\n5. Total users in database: {user_count}")
                    
                else:
                    print("   ❌ Table 'users' NOT found!")
                    print(f"   Please import the schema from database/schema.sql")
            else:
                print(f"   ❌ Database '{db_name}' NOT found!")
                print(f"   Create it with: CREATE DATABASE {db_name};")
                print(f"   Then import schema from database/schema.sql")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"   ❌ Connection failed!")
        print(f"   Error: {e}")
        print(f"\n   Possible solutions:")
        print(f"   1. Check if MySQL server is running")
        print(f"   2. Verify the database credentials in .env file")
        print(f"   3. Make sure the password doesn't contain special characters (use quotes if needed)")
        print(f"   4. Try connecting manually: mysql -h {db_host} -u {db_user} -p")
    
    print("\n" + "=" * 60)
    print("For detailed setup instructions, see SETUP_ADMIN_CREDENTIALS.md")
    print("=" * 60)

if __name__ == "__main__":
    check_mysql_status()
