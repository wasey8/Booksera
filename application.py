from flask import Flask, session,request,render_template,flash,url_for,redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt

#---setting up flask and sessions
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setting up database
engine = create_engine('postgresql://postgres:wasey@localhost/booksera')
db = scoped_session(sessionmaker(bind=engine))


# Homepage
@app.route("/")
def home():
    return render_template("home.html")

#Home page publisher
@app.route('/publisherLogin')
def home2():
    return render_template("home2.html")

#---for admin
@app.route("/admin")
def admin():
    return render_template("admin.html")



#Login page for buyer
@app.route("/hello",  methods=["POST","GET"])
def hello():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session['username']=username
        data=db.execute("SELECT username FROM buyer WHERE username=:username",{"username":username}).fetchone()
        data2=db.execute("SELECT password FROM buyer WHERE username=:username",{"username":username}).fetchone()

        if data is None and data2 is None:
            flash("Incorrect credentials")
            return redirect(url_for('home'))
        else:
            flash("Login successfull!")
            return render_template("hello.html",username=username)
    return render_template("home.html")



#Signup Page for buyer
@app.route("/signup", methods=["GET","POST"])
def sign():
    if request.method=="POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone= request.form.get("phone")
        usernamedata=db.execute("SELECT username FROM buyer WHERE username=:username",{"username":username}).fetchone()
        usernamedata1=db.execute("SELECT email FROM buyer WHERE email=:email",{"email":email}).fetchone()
        usernamedata2=db.execute("SELECT password FROM buyer WHERE password=:password",{"password":password}).fetchone()

        if usernamedata is None and usernamedata1 is None and usernamedata2 is None :
            db.execute("INSERT INTO buyer(username,email,phone,password) VALUES(:username,:email,:phone,:password)",
            {"username":username,"email":email,"phone":phone,"password":password})
            db.commit()
            flash("Account created successfully!")
            return redirect(url_for('home'))
        else:
            flash("Try different credentials")
            return redirect(url_for('sign'))
    return render_template("signup.html")



#Logout for buyer
@app.route("/logout")
def logout():
     if 'username' in session:
         session.pop('username',None)
         flash("logout successfull!")
         return redirect(url_for('home'))


#Logout for seller
@app.route("/logout2")
def logout2():
     if 'username' in session:
         session.pop('username',None)
         flash("logout successfull!")
         return redirect(url_for('home2'))


#Logout for admin
@app.route("/logoutadmin")
def logoutadmin():
    session.pop('username',None)
    flash("logout successfull!")
    return redirect(url_for('admin'))


#Searching for books
@app.route("/search",  methods=["POST","GET"])
def search():
    if request.method=="POST":
         isbn=request.form.get("isbn").lower().strip()
         title=request.form.get("title").lower().strip()
         author=request.form.get("author").lower().strip()
         books=db.execute("SELECT * FROM buyer_view where LOWER(isbn) like :isbn and LOWER(title) like :title and LOWER(author) like :author", {"isbn": f"%{isbn}%","title": f"%{title}%","author":f"%{author}%" }).fetchall()
         return render_template("books.html",books=books, isbn=isbn,author=author,title=title)
    return render_template("hello.html")



#For reviews
@app.route("/review/<isbn>", methods=["GET", "POST"])
def review(isbn):
    session["reviews"]=[]
    if request.method == "POST":
        user_review = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn",
                            {"username": session["username"], "isbn": isbn} )
        userreview = user_review.first()
        if not userreview:
            review = request.form.get("review")
            rating = request.form.get("rating")
            db.execute("INSERT INTO reviews (review, isbn, rating, username) VALUES (:review, :isbn, :rating, :username)",
                        {"review": review, 'isbn': isbn, "rating": rating, "username": session["username"]})
            db.commit()
        else:
            flash('You have already submitted review for this book')
            return redirect(url_for('review',isbn=isbn))
        return redirect(url_for("review", isbn=isbn))
    else:
        book = db.execute("SELECT isbn, title, author, year,price FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
        reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn",{"isbn": isbn}).fetchall()
    return render_template("review.html", book=book , reviews=reviews)


#---Publisher signup
@app.route("/publisher_signup",methods=["GET","POST"])
def publish():
    if request.method=="POST":
        username = request.form.get("username")
        address = request.form.get("email")
        password = request.form.get("password")
        phone= request.form.get("phone")
        usernamedata=db.execute("SELECT username FROM publisher WHERE username=:username",{"username":username}).fetchone()
        usernamedata1=db.execute("SELECT address FROM publisher WHERE address=:address",{"address":address}).fetchone()
        usernamedata2=db.execute("SELECT password FROM publisher WHERE password=:password",{"password":password}).fetchone()
        hash=sha256_crypt.hash(password)

        if usernamedata is None and usernamedata1 is None and usernamedata2 is None :
            db.execute("INSERT INTO publisher(username,phone,address,password) VALUES(:username,:phone,:address,:password)",
            {"username":username,"phone":phone,"address":address,"password":hash})
            db.commit()
            flash("Account created successfully!")
            return redirect(url_for('home2'))
        else:
            flash("Try different credentials")
            return redirect(url_for('publish'))
    return render_template("publisher_sign.html")

#---Publisher log in
@app.route("/publisher_login",  methods=["POST","GET"])
def publisher_login():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session['username']=username
        data=db.execute("SELECT username FROM publisher WHERE username=:username",{"username":username}).fetchone()
        data2=db.execute("SELECT password FROM publisher WHERE username=:username",{"username":username}).fetchone()

        if data is None:
            flash("Incorrect username")
            return redirect(url_for('home2'))
        else:
            for i in data2:
                if sha256_crypt.verify(password,i):
                    flash("Login successfull!")
                    return render_template("publisher_login.html",username=username)
                flash("Invalid password")
                return redirect(url_for('home2'))
    return render_template("home2.html")


#Books publish
@app.route('/publish',methods=["POST","GET"])
def publish_book():
    if request.method=="POST":
        author=request.form.get("author").lower()
        isbn=request.form.get("isbn")
        year=request.form.get("year")
        details=request.form.get("details")
        title=request.form.get("title")
        price=request.form.get("price")
        var2=db.execute("SELECT isbn FROM publish WHERE isbn=:isbn",{"isbn":isbn}).fetchone()
        var3=db.execute("SELECT title FROM publish WHERE title=:title",{"title":title}).fetchone()
        #var4=db.execute("SELECT * FROM publish WHERE author=:author",{"author":author}).fetchall()

        if var2 is None and var3 is None:
            db.execute("INSERT INTO publish(author,isbn,year,details,title,price) VALUES(:author,:isbn,:year,:details,:title,:price)",
            {"author":author,"isbn":isbn,"year":year,"details":details,"title":title,"price":price})
            db.commit()
            flash("Book submitted to admin successfully!")
            return render_template("publisher_login.html",username=author)
        else:
            flash("Book is already submitted, check credentials again.")
            return render_template("publisher_login.html",username=author)
    return render_template("publisher_login.html")


#------buy books
@app.route('/buy/<isbn>,<title>,<price>',methods=["POST","GET"])
def buy(isbn,title,price):
    username=session['username']
    currentbook=isbn
    book_price=price
    if request.method=="POST":
        address=request.form.get("address")
        phone=request.form.get("phone")
        quantity=request.form.get("quantity")
        total=int(quantity)*int(book_price)
        card_no=request.form.get("card_no")
        pin=request.form.get("pin")
        db.execute("INSERT INTO books_order(username,address,phone,isbn,quantity) VALUES(:username,:address,:phone,:isbn,:quantity)",
        {"username":username,"address":address,"phone":phone,"isbn":currentbook,"quantity":quantity})
        db.commit()
        order_id=db.execute("SELECT order_id from books_order where username=:username",{"username":username}).fetchone()
        order_id=order_id[0]
        db.execute("INSERT into payment_details(order_id,card_no,pin) values(:order_id,:card_no,:pin)",{"order_id":order_id,"card_no":card_no,"pin":pin})
        db.commit()
        flash("Successfully ordered")
        return render_template("invoice.html",book=currentbook,username=username,title=title,price=price,total=total,quantity=quantity,order_id=order_id)
    return render_template("buy.html",book=currentbook,username=username,title=title,price=price)



#--For admin panel
@app.route('/admin_panel',methods=["POST","GET"])
def admin_main():
    if request.method=="POST":
        password=request.form.get("password")
        username=request.form.get("username")
        data1=db.execute("SELECT username from admin where username=:username",{"username":username}).fetchone()
        data2=db.execute("SELECT password from admin where username=:username",{"username":username}).fetchone()

        if data1 is None and data2 is None:
            flash("Incorrect credentials")
            return redirect(url_for('admin_main'))
        else:
            flash("Login successfull!")
            publishers=db.execute("SELECT * from admin_view_publish").fetchall()

            db.commit()
            return render_template("adminmain.html",username=username,publishers=publishers)
    return render_template("admin.html")



#---user_books
@app.route('/books/<username>')
def user_books(username):
    books=db.execute(f"SELECT * from publisher_books('{username}')" ).fetchall()
    count=db.execute(f"SELECT count(*) from publisher_books('{username}')" ).fetchone()
    db.commit()
    for i in count:
        count=int(i)
        return render_template("user_books.html",username=username,books=books,count=count)
    return render_template("user_books.html",username=username)



#---approve books
@app.route('/approvebook/<book_isbn>')
def approve_book(book_isbn):
    book_isbn=book_isbn
    title=db.execute('select title from publish where isbn=:isbn',{'isbn':book_isbn}).fetchone()
    author=db.execute('select author from publish where isbn=:isbn',{'isbn':book_isbn}).fetchone()
    price=db.execute('select price from publish where isbn=:isbn',{'isbn':book_isbn}).fetchone()
    year=db.execute('select year from publish where isbn=:isbn',{'isbn':book_isbn}).fetchone()
    title=title[0]
    author=author[0]
    price=price[0]
    year=year[0]
    db.commit()

    if book_isbn is None:
        flash('Book is already approved')
        return redirect(url_for('admin_main'))
    else:
        db.execute('INSERT into books (isbn,author,year,title,price) values (:isbn,:author,:year,:title,:price)',{'isbn':book_isbn,'author':author,'year':year,'title':title,'price':price})
        db.commit()
        db.execute('Delete from publish where isbn=:isbn',{'isbn':book_isbn})
        db.commit()
        flash('Book approved successfully')
        return render_template('adminmain.html')


#---delete book
@app.route('/deletebook/<book_isbn>')
def delete_book(book_isbn):
    book_isbn=book_isbn
    db.execute('Delete from publish where isbn=:isbn',{'isbn':book_isbn})
    db.commit()
    flash('Book removed successfully')
    return render_template('adminmain.html')



#Main function
if __name__==("__main__"):
    app.run(debug=True)

