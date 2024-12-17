from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # 查询用户是否存在
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            # 如果用户存在，检查密码
            if check_password_hash(user[0], password):
                session['username'] = '账号'
                return redirect(url_for('home'))
            else:
                return "密码错误，请重试！"
        else:
            # 如果用户不存在，跳转到注册页面
            return redirect(url_for('register'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("-------------------"*3)
        print(request.form)
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except Exception as e:
            print("注册错误：", e)
            return "用户名已存在！"
        finally:
            conn.close()
    return render_template('register.html')

# 主页
@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    print("request method=======================")
    print(request.method)
    if 'username' not in session:
        return redirect(url_for('register'))
    if request.method == 'POST':
        try:
            # 从表单中获取数据
            student_number = request.form['student_number']
            name = request.form['name']
            age = request.form['age']
            department = request.form['department']
            graduation_status = request.form['graduation_status']
            employment = request.form['employment']
            
            # 插入数据到数据库
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (student_number, name, age, department, graduation_status, employment) VALUES (?, ?, ?, ?, ?, ?)",
                           (student_number, name, age, department, graduation_status, employment))
            conn.commit()
            print("insert into database success=====")
        except Exception as e:
            print("数据库插入错误：", e)
            return "插入数据时发生错误"
        finally:
            conn.close()
        return redirect(url_for('home'))
    return render_template('add_student.html')
@app.route('/view_students', methods=['GET'])
def view_students():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT student_number, name, age, department, graduation_status, employment FROM students")
        students = cursor.fetchall()
        conn.close()
        return render_template('view_students.html', students=students)
    except Exception as e:
        print("数据库查询错误：", e)
        return "查询学生信息时发生错误"
    
@app.route('/update_student/<student_number>', methods=['GET', 'POST'])
def update_student(student_number):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        try:
            # 从表单中获取更新后的数据
            name = request.form['name']
            age = request.form['age']
            department = request.form['department']
            graduation_status = request.form['graduation_status']
            employment = request.form['employment']

            # 更新数据库中的学生信息
            cursor.execute("""
                UPDATE students
                SET name=?, age=?, department=?, graduation_status=?, employment=?
                WHERE student_number=?
            """, (name, age, department, graduation_status, employment, student_number))
            conn.commit()
        except Exception as e:
            print("数据库更新错误：", e)
            return "更新学生信息时发生错误"
        finally:
            conn.close()
        return redirect(url_for('view_students'))
    
    # 获取学生的现有信息
    cursor.execute("SELECT student_number, name, age, department, graduation_status, employment FROM students WHERE student_number=?", (student_number,))
    student = cursor.fetchone()
    conn.close()

    if not student:
        return "未找到该学生的信息"

    # 渲染更新页面
    return render_template('update_student.html', student=student)

@app.route('/delete_student/<student_number>', methods=['GET', 'POST'])
def delete_student(student_number):
    # 检查用户是否已登录
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        # 显示确认删除的页面
        return render_template('confirm_delete.html', student_number=student_number)

    elif request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # 查询学生是否存在
        cursor.execute("SELECT * FROM students WHERE student_number = ?", (student_number,))
        student = cursor.fetchone()

        if student:
            # 如果学生存在，执行删除操作
            cursor.execute("DELETE FROM students WHERE student_number = ?", (student_number,))
            conn.commit()
            conn.close()
            # 删除成功后重定向到首页
            return redirect(url_for('home'))
        else:
            conn.close()
            return f"学生 {student_number} 不存在", 404


if __name__ == '__main__':
    app.run(debug=True)
# 添加学生页面
