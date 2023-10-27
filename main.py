from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
import os
import bcrypt

app = Flask(__name__)
app.secret_key=os.urandom(24)  #secret key for session

#mysql Connector
conn = mysql.connector.connect(host='localhost',
                                user='root',
                                password='',
                                database='userdetails')
cursor = conn.cursor()

#homepage
@app.route("/")
def homepage():
    return render_template('login.html')

#rediret to signup page
@app.route('/signup')
def signupdata():
    return render_template("signup.html")

#redirecting to login page
@app.route('/login')
def loginpage():
    return render_template('login.html')

#profile for the user
@app.route('/profilepage')
def profile_page():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return render_template('profile.html', user=user)
        else:
            return redirect('/login')

#retrieving login values
@app.route('/loginvalues', methods=['GET','POST'])
def login_value():
    if request.method == 'POST':
        username = request.form.get('usn')
        password = request.form.get('psw')
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if user:
            stored_password = user[4]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session['user_id'] = user[0]
                return redirect('/profilepage')
        flash("Login failed, Please Check your Username and Password")
        return redirect('/login')
    return render_template('login.html')
    
    #retrieve sigup details
@app.route('/signupvalue', methods=['GET','POST'])
def signup_value():
    if request.method == 'POST':
        name=request.form.get('nm')
        username=request.form.get('usn')
        email = request.form.get('eml')
        password = request.form.get('psw')
        cpassword = request.form.get('cpsw')
        pencrypted= bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        cpencrypted = bcrypt.hashpw(cpassword.encode('utf-8'),bcrypt.gensalt())
        if password != cpassword:
            flash("password not matched")
            return redirect('/signup')
        else:
            cursor.execute(f"SELECT * FROM users where username='{username}'")
            users=cursor.fetchone()
            if users:
                flash("user already exists")
                return redirect('/signup')
            else:
                cursor.execute("INSERT INTO users(name,username,email,password,cpassword) VALUES(%s,%s,%s,%s,%s)",(name,username,email,pencrypted,cpencrypted))
                conn.commit
                conn.close
                flash("Signup complete")
                return redirect('/signup')
    # return redirect('/signup')

#LOOGOUT FUNCTION
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

#delete function
@app.route('/delete')
def delete_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        flash("profile deleted")
        return redirect('/login')
if __name__ == "__main__":
    app.run(debug=True)