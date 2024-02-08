from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'many random bytes'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crud'

mysql = MySQL(app)

# Initialize JWT
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['SECRET_KEY'] = 'YOU_SECRET_KEY'
jwt = JWTManager(app)

# Route to render the index/login page
@app.route('/')
def Index():
    # Fetch data from the users table
    cur_users = mysql.connection.cursor()
    cur_users.execute("SELECT * FROM users")
    users_data = cur_users.fetchall()
    cur_users.close()

    # Fetch data from the students table
    cur_students = mysql.connection.cursor()
    cur_students.execute("SELECT * FROM students")
    students_data = cur_students.fetchall()
    cur_students.close()

    return render_template('login.html', users=users_data, students=students_data)

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save user data to the users database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash("Registration successful! Please log in", "success")  # Flash success message
        return redirect(url_for('Index'))  # Redirect to login after successful registration

    return render_template('register.html')

# User login route
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists and password is correct
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):  # Assuming the password is at index 2
            # Successful login
            flash("Login Successful!")
            # Redirect to the dashboard after successful login
            return redirect(url_for('dashboard'))

        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('Index'))  # Redirect back to login with error message

    return render_template('login.html')  # Render the login page if it's a GET request

# Dashboard to show student data
@app.route('/dashboard')
def dashboard():
    cur_students = mysql.connection.cursor()
    cur_students.execute("SELECT * FROM students")
    students_data = cur_students.fetchall()
    cur_students.close()

    return render_template('index.html', students=students_data)

# Route to insert new student data
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
        mysql.connection.commit()
        return redirect(url_for('dashboard'))

# Route to delete a student record
@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('dashboard'))

# Route to update student data
@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET name=%s, email=%s, phone=%s WHERE id=%s", (name, email, phone, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
