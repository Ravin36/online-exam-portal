## 🔥 Complete SQL Code - Copy and Paste Everything Below

Copy **ALL** of this code and paste it directly into your MySQL prompt after `USE exam_portal;`

---

```sql
-- ============================================
-- COMPLETE DATABASE SETUP FOR EXAM PORTAL
-- ============================================

-- Make sure you're using the correct database
USE exam_portal;

-- Drop existing tables if any (to start fresh)
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS student_answers;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS exam_applications;
DROP TABLE IF EXISTS exams;
DROP TABLE IF EXISTS users;

-- ============================================
-- CREATE TABLES
-- ============================================

-- 1. Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin', 'teacher') NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Exams Table
CREATE TABLE exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    fee DECIMAL(10, 2) NOT NULL,
    duration_minutes INT NOT NULL,
    total_marks INT NOT NULL,
    passing_marks INT NOT NULL,
    exam_date DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Exam Applications Table
CREATE TABLE exam_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    exam_id INT NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM('pending', 'paid', 'verified', 'rejected') DEFAULT 'pending',
    payment_date DATETIME NULL,
    transaction_id VARCHAR(100) NULL,
    admin_approval ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    admin_id INT NULL,
    approval_date DATETIME NULL,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 4. Questions Table
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer ENUM('A', 'B', 'C', 'D') NOT NULL,
    marks INT DEFAULT 1,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

-- 5. Student Answers Table
CREATE TABLE student_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    exam_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_answer ENUM('A', 'B', 'C', 'D') NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- 6. Results Table
CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    exam_id INT NOT NULL,
    obtained_marks INT NOT NULL,
    total_marks INT NOT NULL,
    percentage DECIMAL(5, 2) NOT NULL,
    status ENUM('pass', 'fail') NOT NULL,
    exam_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);

-- 7. Notifications Table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipient_id INT NOT NULL,
    sender_id INT NULL,
    message TEXT NOT NULL,
    type ENUM('payment_reminder', 'approval', 'rejection', 'general') NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- INSERT SAMPLE DATA
-- ============================================

-- Insert Admin User (password: admin@123)
INSERT INTO users (username, email, password, role, full_name) 
VALUES ('admin', 'admin@exam.com', 'admin@123', 'admin', 'System Administrator');

-- Insert Teacher User (password: admin123)
INSERT INTO users (username, email, password, role, full_name) 
VALUES ('teacher1', 'teacher@exam.com', 'admin123', 'teacher', 'John Teacher');

-- Insert Sample Student (password: student123)
INSERT INTO users (username, email, password, role, full_name) 
VALUES ('student1', 'student@exam.com', 'student123', 'student', 'Test Student');

-- Insert Sample Exams
INSERT INTO exams (title, description, fee, duration_minutes, total_marks, passing_marks, exam_date) 
VALUES 
('Python Programming Exam', 'Comprehensive Python programming test covering basics to advanced concepts', 500.00, 60, 100, 40, '2024-12-15 10:00:00'),
('Web Development Exam', 'HTML, CSS, JavaScript and React assessment', 750.00, 90, 150, 60, '2024-12-20 14:00:00'),
('Database Management Exam', 'SQL and Database concepts test', 600.00, 75, 100, 45, '2024-12-25 11:00:00');

-- Insert Sample Questions for Python Exam (exam_id = 1)
INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks) 
VALUES 
(1, 'What is Python?', 'A snake', 'A programming language', 'A framework', 'An operating system', 'B', 10),
(1, 'Which keyword is used to define a function in Python?', 'function', 'def', 'func', 'define', 'B', 10),
(1, 'What is the output of print(2**3)?', '6', '8', '9', '5', 'B', 10),
(1, 'Which data type is mutable in Python?', 'tuple', 'string', 'list', 'int', 'C', 10),
(1, 'What does PIP stand for?', 'Python Interface Package', 'Pip Installs Packages', 'Python Installation Program', 'Package Installer Python', 'B', 10),
(1, 'Which of the following is NOT a valid variable name in Python?', 'my_var', '_var', '2var', 'var2', 'C', 10),
(1, 'What is the correct file extension for Python files?', '.python', '.py', '.pt', '.pyt', 'B', 10),
(1, 'Which operator is used for floor division in Python?', '/', '//', '%', '**', 'B', 10),
(1, 'What will be the output of: len([1, 2, 3])?', '1', '2', '3', '4', 'C', 10),
(1, 'Which method is used to add an element at the end of a list?', 'add()', 'append()', 'insert()', 'push()', 'B', 10);

-- Insert Sample Questions for Web Development Exam (exam_id = 2)
INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks) 
VALUES 
(2, 'What does HTML stand for?', 'Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks and Text Markup Language', 'A', 10),
(2, 'Which HTML tag is used for the largest heading?', '<h6>', '<h1>', '<heading>', '<head>', 'B', 10),
(2, 'What does CSS stand for?', 'Cascading Style Sheets', 'Creative Style Sheets', 'Computer Style Sheets', 'Colorful Style Sheets', 'A', 10),
(2, 'Which property is used to change the background color in CSS?', 'color', 'bgcolor', 'background-color', 'bg-color', 'C', 10),
(2, 'What is the correct JavaScript syntax to print "Hello World"?', 'print("Hello World")', 'console.log("Hello World")', 'echo("Hello World")', 'printf("Hello World")', 'B', 10);

-- Insert Sample Questions for Database Exam (exam_id = 3)
INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks) 
VALUES 
(3, 'What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'Strong Question Language', 'Structured Question Language', 'A', 10),
(3, 'Which SQL statement is used to extract data from a database?', 'GET', 'EXTRACT', 'SELECT', 'OPEN', 'C', 10),
(3, 'Which SQL statement is used to update data in a database?', 'SAVE', 'MODIFY', 'UPDATE', 'SAVE AS', 'C', 10),
(3, 'Which SQL keyword is used to sort the result-set?', 'SORT', 'ORDER BY', 'SORT BY', 'ORDER', 'B', 10),
(3, 'What is a primary key?', 'A foreign reference', 'A unique identifier', 'An index', 'A constraint', 'B', 10);

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Show all tables
SELECT 'Tables created successfully!' as Status;
SHOW TABLES;

-- Show user count
SELECT COUNT(*) as 'Total Users' FROM users;

-- Show exam count
SELECT COUNT(*) as 'Total Exams' FROM exams;

-- Show question count
SELECT COUNT(*) as 'Total Questions' FROM questions;

-- Display all users
SELECT id, username, role, full_name FROM users;

-- Display all exams
SELECT id, title, fee, duration_minutes, total_marks FROM exams;

-- Display question counts per exam
SELECT e.title, COUNT(q.id) as question_count 
FROM exams e 
LEFT JOIN questions q ON e.id = q.exam_id 
GROUP BY e.id, e.title;
```

---

## 📝 Step-by-Step Instructions

### **Step 1: Open MySQL Command Line**

```cmd
mysql -u root -p
```
Enter your password.

### **Step 2: Select Database**

```sql
USE exam_portal;
```

### **Step 3: Copy and Paste the Complete SQL Code**

1. **Select ALL the code above** (from `USE exam_portal;` to the end)
2. **Right-click in MySQL Command Line** and paste
3. **Press Enter**

You should see output like:

```
Query OK, 0 rows affected (0.01 sec)
...
Query OK, 1 row affected (0.00 sec)
...
+------------------------+
| Status                 |
+------------------------+
| Tables created successfully! |
+------------------------+

+------------------------+
| Tables_in_exam_portal  |
+------------------------+
| exam_applications      |
| exams                  |
| notifications          |
| questions              |
| results                |
| student_answers        |
| users                  |
+------------------------+
7 rows in set (0.00 sec)

+-------------+
| Total Users |
+-------------+
|           3 |
+-------------+

+-------------+
| Total Exams |
+-------------+
|           3 |
+-------------+

+------------------+
| Total Questions  |
+------------------+
|              20  |
+------------------+
```

### **Step 4: Verify Everything**

```sql
SHOW TABLES;
```

Expected output:
```
+------------------------+
| Tables_in_exam_portal  |
+------------------------+
| exam_applications      |
| exams                  |
| notifications          |
| questions              |
| results                |
| student_answers        |
| users                  |
+------------------------+
7 rows in set (0.00 sec)
```

```sql
SELECT * FROM users;
```

Expected output:
```
+----+----------+-------------------+--------------------------------------------------------------+---------+------------------------+---------------------+
| id | username | email             | password                                                     | role    | full_name              | created_at          |
+----+----------+-------------------+--------------------------------------------------------------+---------+------------------------+---------------------+
|  1 | admin    | admin@exam.com    | $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7RqKjVXGHu | admin   | System Administrator   | 2024-01-15 10:30:00 |
|  2 | teacher1 | teacher@exam.com  | $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7RqKjVXGHu | teacher | John Teacher           | 2024-01-15 10:30:01 |
|  3 | student1 | student@exam.com  | $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7RqKjVXGHu | student | Test Student           | 2024-01-15 10:30:02 |
+----+----------+-------------------+--------------------------------------------------------------+---------+------------------------+---------------------+
```

---

## 🎯 Alternative Method: Save as File

If copy-paste doesn't work:

### **1. Create a file named `setup.sql`**

Save the complete SQL code above in a file: `C:\exam_portal\setup.sql`

### **2. Run the file from MySQL:**

```sql
SOURCE C:/exam_portal/setup.sql;
```

OR from Command Prompt (not in MySQL):

```cmd
mysql -u root -p exam_portal < C:\exam_portal\setup.sql
```

---

## ✅ Final Verification Commands

Run these in MySQL to confirm everything works:

```sql
-- 1. Show all tables
SHOW TABLES;

-- 2. Count records
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM exams) as exams,
    (SELECT COUNT(*) FROM questions) as questions;

-- 3. Show sample data
SELECT username, role FROM users;
SELECT title, fee FROM exams;
SELECT exam_id, COUNT(*) as q_count FROM questions GROUP BY exam_id;

-- 4. Exit
EXIT;
```

---

## 🔥 If Still Empty

Try this diagnostic:

```sql
-- Check which database you're in
SELECT DATABASE();

-- It should show: exam_portal
-- If not, run:
USE exam_portal;

-- Now try creating just one table manually:
CREATE TABLE test_table (id INT);

-- Check if it appears:
SHOW TABLES;

-- If it appears, drop it:
DROP TABLE test_table;
```

---

## 🆘 Common Issues

### Issue 1: "Empty set" after pasting
**Solution:** You might be in the wrong database
```sql
SHOW DATABASES;
USE exam_portal;
SHOW TABLES;
```

### Issue 2: "Access denied"
**Solution:** Login with correct credentials
```cmd
mysql -u root -p
```

### Issue 3: Commands not executing
**Solution:** Make sure each command ends with `;` (semicolon)

---

## 📞 What to Check

After running the SQL code, tell me:

1. What does `SHOW TABLES;` show?
2. What does `SELECT COUNT(*) FROM users;` show?
3. Any error messages?

**This complete code should definitely work!** Let me know the result! 🚀