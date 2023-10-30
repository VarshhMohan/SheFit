#--------------------------------------------------------Import Libraries------------------------------------------------------------------#
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sqlalchemy")

from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, date






#---------------------------------------------------Default objects creation----------------------------------------------------------------#
#region
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'

db = SQLAlchemy(app)
ph = PasswordHasher()
login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = ph.hash("triggervarning")

@login_manager.user_loader
def load_user(user_id):
    # Check if the user is an admin
    admin = Admin.query.get(user_id)
    # If the user is not an admin, check if they are a regular member
    if admin is None:
        member = Members.query.get(user_id)
        # If the user is not a regular member, check if they are a trainer
        if member is None:
            trainer = Trainers.query.get(user_id)
            return trainer  # Return the trainer user if found
        return member  # Return the regular member user if found
    return admin  # Return the admin user if found
#endregion

#----------------------------------------------------------Classes--------------------------------------------------------------------------#
#region
class Package(db.Model):
    pkg_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))
    duration = db.Column(db.Integer)
    feature_coach = db.Column(db.Boolean)
    feature_dietician = db.Column(db.Boolean)
    feature_lounge = db.Column(db.Boolean)
    feature_courses = db.Column(db.Boolean)
    feature_schedules = db.Column(db.Boolean)
    price = db.Column(db.Integer)

    def __init__(self, name, duration, coach, dietician, lounge, courses, schedules, price):
        self.name = name
        self.duration = duration
        self.feature_coach = coach
        self.feature_dietician = dietician
        self.feature_lounge = lounge
        self.feature_courses = courses
        self.feature_schedules = schedules
        self.price = price
        db.session.add(self)
        db.session.commit()

    
    def delete(id):
        del_pkg = Package.query.get(id)
        db.session.delete(del_pkg)
        db.session.commit()
    
    def modify(self,name,duration,description,price):
        self.name = name
        self.duration = duration
        self.description = description
        self.price = price
        db.session.commit()


class Subscription(db.Model):
    subscription_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    pkg_id = db.Column(db.Integer)
    mem_id = db.Column(db.String(10))
    tra_id = db.Column(db.String(10))
    completed = db.Column(db.Integer)

    def __init__(self,pkg_id,mem_id,tra_id):
        self.pkg_id = pkg_id
        self.mem_id = mem_id
        self.tra_id = tra_id
        self.completed = 0
        db.session.add(self)
        db.session.commit()
    


class Members(db.Model,UserMixin):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))  
    email = db.Column(db.String(100), nullable=False)
    member_since = db.Column(db.DateTime)
    password = db.Column(db.String(128), nullable=False)
    
    def __init__(self, name, phone_number, email, password, member_since):
        last_mem = Members.query.order_by(Members.id.desc()).first()
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.member_since = member_since
        self.password = ph.hash(password)
        last_id=0
        if last_mem:
            last_id = int(last_mem.id[3:])
        self.id = f"mem{last_id+1}"

    def register(self):
        db.session.add(self)
        db.session.commit()
  

class Trainers(db.Model,UserMixin):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(100))
    trainer_since = db.Column(db.DateTime)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, phone_number, email, password, experience):
        last_train = Trainers.query.order_by(Trainers.id.desc()).first()
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.trainer_since = datetime.now()
        self.experience = experience
        self.password = ph.hash(password)
        last_id=0
        if last_train:
            last_id = int(last_train.id[3:])
        self.id = f"tra{last_id+1}"

    def list_trainers():
        trainer_list = Trainers.query.all()
        return trainer_list
    
    def delete(id):
        del_trainer = Trainers.query.get(id)
        db.session.delete(del_trainer)
        db.session.commit()

    def modify(self, name, phone_number, email, experience):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.experience = experience
        db.session.commit()


class Admin(db.Model,UserMixin):
    id   = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, phone_number, email, password):
        last_adm = Admin.query.order_by(Admin.id.desc()).first()
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.password = ph.hash(password)
        last_id=0
        if last_adm:
            last_id = int(last_adm.id[3:])
        self.id  = f"adm{last_id+1}"


class DietPro(db.Model):
    dietid   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    member_id = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    activity = db.Column(db.String(50))
    health = db.Column(db.String(200))
    daily_calorie = db.Column(db.Float)
    
    def __init__(self,name,gender,age,weight,height,activity,health,member_id=None):
        self.name = name
        self.gender = gender
        self.age = age
        self.weight = weight
        self.height = height
        self.activity = activity
        self.health = health
        self.member_id = member_id
    
    def set_goal(self):
        #find user's Basal Metabolic Rate
        bmr = 0.0
        if self.gender=='Female':
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)
        else:
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)

        #calculating users Total Daily Energy Expenditure
        activity_mapping = {
            'sedentary' : 1.2,
            'lightly active' : 1.375,
            'moderately active' : 1.55,
            'very active' : 1.725
        }
        activity_val = activity_mapping[self.activity]

        tdee = bmr * activity_val
        #calculate weight goal
        bmi = self.weight * 10000 / (self.height ** 2)

        weight_goal = 0.0
        if bmi>24.9:
            weight_goal = 24.9 * (self.height ** 2) / 10000
        elif bmi<18.5:
            weight_goal = 18.9 * (self.height ** 2) / 10000
        else:
            weight_goal = 0.0

        #calculate users calorie goal for daily intake
        calorie_change = 108.7573 * (weight_goal - self.weight)
        self.daily_calorie = tdee + calorie_change

class Payments(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float)
    payment_date = db.Column(db.Date)
    subscription_id = db.Column(db.Integer)

class CardPayment(Payments):
    card_number = db.Column(db.String(16))
    card_holder = db.Column(db.String(255))
    expiration_date = db.Column(db.String(5))

    def __init__(self,amount,subs_id,card_number,card_holder,exp):
        super().__init__(amount=amount, payment_date=date.today(), subscription_id = subs_id)
        self.card_number = card_number
        self.card_holder = card_holder
        self.expiration_date = exp
        db.session.add(self)
        db.session.commit()

class CashPayment(Payments):
    cash_receipt_number = db.Column(db.String(10))

    def __init__(self,amount,subs_id,r_no):
        super().__init__(amount=amount, payment_date=date.today(), subscription_id = subs_id)
        self.cash_receipt_number = r_no
        db.session.add(self)
        db.session.commit()

class UPIPayment(Payments):
    upi_id = db.Column(db.String(50))

    def __init__(self,amount,subs_id, upi_id):
        super().__init__(amount=amount, payment_date=date.today(), subscription_id = subs_id)
        self.upi_id = upi_id
        db.session.add(self)
        db.session.commit()


        


#endregion

#--------------------------------------------------------Routing Member----------------------------------------------------------------------#
#region
#home page
@app.route('/')
def homepage():
    packages = Package.query.all()
    member=current_user
    if isinstance(member,Members):
        return render_template('index.html', pkgs=packages, member=member)
    else:
        return render_template('index.html', pkgs=packages)

#Member registration
@app.route('/register', methods=["GET", "POST"])
def register():
    member = current_user
    if isinstance(member,Members):
        return redirect(url_for('dashboard'))
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        password = request.form.get("password")
        # Check if a user with the same email already exists
        existing_member = Members.query.filter_by(email=email).first()

        if existing_member:
            return render_template("signup.html",message_id=1)
        else:
            # Set the "member_since" date to the current date
            member_since = datetime.now()

            # Create a new member
            member = Members(
                name=name,
                phone_number=phone_number,
                email=email,
                password=password,
                member_since=member_since
            )
            member.register()
            return redirect(url_for("login"))
    
    return render_template("signup.html",message_id=0)



#Member login
@app.route("/login", methods=["GET", "POST"])
def login():
    member = current_user
    if isinstance(member,Members):
        return redirect(url_for('dashboard'))
    if request.method == "POST":
        member = Members.query.filter_by(email=request.form.get("email")).first()
        password = request.form.get("password")
        if not member:
            return render_template("login.html", message="User Not registered")
        try:
            if member and ph.verify(member.password, password):
                # The entered password matches the stored hashed password
                login_user(member)
                print("login")
                return redirect(url_for("dashboard"))
        except VerifyMismatchError:
            # Password doesn't match or user not found
            print("wrong pass")
            return render_template("login.html", message="Wrong Password")
    return render_template("login.html")

#user dashboard
@app.route("/dashboard")
def dashboard():
    member = current_user
    if not isinstance(member,Members):
        return redirect(url_for("login"))
    
    subscription = Subscription.query.filter_by(mem_id=member.id).first()
    return render_template('dashboard.html',member=member,subscription=subscription)


@app.route('/payment/<int:id>',methods=["GET","POST"])
def payment(id):
    member = current_user
    if not isinstance(member,Members):
        return redirect(url_for('login'))
    if request.method == 'GET':
        package = Package.query.get(id)
        return render_template('payment.html',package=package)
    else:
        payment_mode = request.form.get('payment_mode')
        pkg_id = request.form.get('pkgid')
        package = Package.query.get(pkg_id)
        amt = package.price
        subscription = Subscription(pkg_id,member.id,None)
        subs_id = subscription.subscription_id
        success = {'type':payment_mode}
        if payment_mode == "card":
            name = request.form.get('name')
            card_number = request.form.get('card_number')
            exp_date = request.form.get('exp_date')
            cvv = request.form.get('cvv')
            CardPayment(package.price, subs_id,card_number,name,exp_date)

        elif payment_mode == "cash":
            receipt = CashPayment(package.price,subs_id,'not_paid')
            r_no = receipt.payment_id
            success['r_no']=r_no

        elif payment_mode == "upi":
            upi_id = request.form.get('upi_id')
            UPIPayment(package.price,subs_id,upi_id)
        return render_template('payment.html',success=success)
        


#DietPro™
@app.route("/dietpro",methods=["GET","POST"])
def dietpro():
    if request.method == 'POST':
        name = request.form.get("name")
        gender = request.form.get("gender")
        age = int(request.form.get("age"))
        weight = float(request.form.get("weight"))
        height = float(request.form.get("height"))
        activity = request.form.get("activity")
        health = request.form.get("health")

        dietpro = DietPro(name,gender,age,weight,height,activity,health)
        dietpro.set_goal()
        return str(dietpro.daily_calorie)
    return render_template('dietpro.html')

#DietPro Result
@app.route("/dietpro/result",methods=["GET","POST"])
def dietpro_result():
    return 2

#user logout
@app.route("/logout")
def logout():
    member = current_user
    if isinstance(member,Members):
        logout_user()
        return redirect(url_for("homepage"))
#endregion

#-------------------------------------------------------Routing Trainer----------------------------------------------------------------------#
#region
#trainer login
@app.route("/trainer/login", methods=["GET", "POST"])
def trainer_login():
    trainer = current_user
    if isinstance(trainer,Trainers):
        return redirect(url_for('trainer_dashboard'))
    if request.method == "POST":
        trainer = Trainers.query.filter_by(email=request.form.get("email")).first()
        password = request.form.get("password")
        try:
            if trainer and ph.verify(trainer.password, password):
                # The entered password matches the stored hashed password
                login_user(trainer)
                print("login")
                return redirect(url_for("trainer_dashboard"))
        except VerifyMismatchError:
            # Password doesn't match or user not found
            print("wrong pass")
            return render_template("login.html", message="Invalid email or password")
    return render_template("login.html")



# trainer dashboard
@app.route('/trainer/dashboard')
def trainer_dashboard():
    trainer = current_user
    if isinstance(trainer,Trainers):
        return trainer.email
    return redirect(url_for("trainer_login"))



#trainer logout
@app.route("/trainer/logout")
def trainer_logout():
    trainer = current_user
    if isinstance(trainer,Trainers):
        logout_user()
        return redirect(url_for("homepage"))

#endregion


#-------------------------------------------------------Routing Admin------------------------------------------------------------------------#
#region
#developement testing
@app.route('/temp')
def temp():
    all_records = Members.query.all()
    s=""
    for i,record in enumerate(all_records):
        s+=str(i)+str(record.__dict__)+'\n\t\t\t\t\t\t\t\t'
    return s

#create tables for db
@app.route('/admin/create_tables', methods=["POST","GET"])
def create_tables():
    if request.method == "POST":
        passwd = request.form.get("passwd")
        if ph.verify(app.config['SECRET_KEY'],passwd):
            with app.app_context():
                db.create_all()
            return 'Database tables created successfully!'
        else:
            return 'Wrong Password'
    return render_template('dev_tools.html',tool_id=0)


#create admin
@app.route('/admin/create_admin', methods=["POST","GET"])
def create_admin():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        password = request.form.get("password")
        dev_pass = request.form.get("dev_password")
        # Check if a user with the same email already exists
        existing_admin = Admin.query.filter_by(email=email).first()

        if existing_admin:
            return render_template("register.html",message_id=1)
        elif ph.verify(app.secret_key,dev_pass):

            # Create a new member
            admin = Admin(
                name=name,
                phone_number=phone_number,
                email=email,
                password=password,
            )

            db.session.add(admin)
            db.session.commit()
            return "created admin"
        else:
            return "error"
    return render_template('dev_tools.html',tool_id=1)



#Admin login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    admin = current_user
    if isinstance(admin,Admin):
        return redirect(url_for('admin_panel'))
    if request.method == "POST":
        admin = Admin.query.filter_by(email=request.form.get("email")).first()
        password = request.form.get("password")
        try:
            if admin and ph.verify(admin.password, password):
                # The entered password matches the stored hashed password
                login_user(admin)
                print("login")
                return redirect(url_for("admin_panel"))
        except VerifyMismatchError:
            # Password doesn't match or user not found
            print("wrong pass")
            return render_template("login.html", message="Invalid email or password")
    return render_template("login.html")


# admin panel
@app.route('/admin/panel')
def admin_panel():
    admin = current_user
    if isinstance(admin,Admin):
        return render_template('admin/index.html',admin=admin)
    return redirect(url_for("admin_login"))

#hire trainer
@app.route('/admin/hire_trainer', methods=["GET","POST"])
def hire_trainer():
    admin = current_user
    if isinstance(admin,Admin):
        if request.method=="POST":
            name = request.form.get("name")
            phone_number = request.form.get("phone_number")
            experience = request.form.get("experience")
            email = request.form.get("email")
            passwd = request.form.get("password")

            existing_trainer = Trainers.query.filter_by(email=email).first()
            if existing_trainer:
                return render_template('/admin/hiretrainer.html', message_id=1,admin=admin)
            else:
                trainer = Trainers(
                    name = name,
                    phone_number = phone_number,
                    experience = experience,
                    email = email,
                    password = passwd
                    )
                
                db.session.add(trainer)
                db.session.commit()
                return redirect(url_for('trainer_manager'))
        return redirect(url_for('trainer_manager'))
    return redirect(url_for('admin_login'))

@app.route('/admin/trainers')
def trainer_manager():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    trainer_list = Trainers.query.all()
    return render_template('/admin/trainers.html',admin=admin,trainers=trainer_list)

@app.route("/admin/trainer/delete", methods=["POST"])
def delete_trainer():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    trainer_id = request.form.get('id')
    Trainers.delete(trainer_id)
    return redirect(url_for('trainer_manager'))

@app.route("/admin/trainer/modify",methods=["GET","POST"])
def modify_trainer():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    id = request.args.get('id')
    trainer = Trainers.query.get(id)

    if request.method == 'POST':
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        experience = request.form.get('experience')
        trainer.modify(name, phone_number, email, experience)


        return redirect(url_for('trainer_manager')) 

    return render_template("/admin/trainer_modify.html",admin=admin, trainer=trainer)


@app.route("/admin/package")
def package_manager():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    package_list = Package.query.all()
    return render_template('/admin/package.html',admin=admin,pkgs=package_list)
    

@app.route("/admin/package/add", methods=["POST"])
def add_package():
    admin = current_user
    if not isinstance(admin, Admin):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form['name']
        duration = int(request.form['duration'])
        feature_coach = 'feature_coach' in request.form
        feature_dietician = 'feature_dietician' in request.form
        feature_lounge = 'feature_lounge' in request.form
        feature_courses = 'feature_courses' in request.form
        feature_schedules = 'feature_schedules' in request.form
        price = int(request.form['price'])

        Package(name, duration, feature_coach, feature_dietician, feature_lounge, feature_courses, feature_schedules, price)
    
    return redirect(url_for('package_manager'))


@app.route("/admin/package/delete", methods=["POST"])
def delete_package():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    package_id = int(request.form.get('id'))
    Package.delete(package_id)
    return redirect(url_for('package_manager'))

@app.route("/admin/package/modify",methods=["GET","POST"])
def modify_package():
    admin = current_user
    if not isinstance(admin,Admin):
        return redirect(url_for('admin_login'))
    id = request.args.get('id')
    package = Package.query.get(id)

    if request.method == 'POST':
        name = request.form.get('name')
        duration = request.form.get('duration')
        description = request.form.get('description')
        price = request.form.get('price')
        package.modify(name,duration,description,price)

        return redirect(url_for('package_manager')) 

    return render_template("/admin/package_modify.html",admin=admin, package=package)

#admin logout
@app.route("/admin/logout")
def admin_logout():
    admin = current_user
    if isinstance(admin,Admin):
        logout_user()
        return redirect(url_for("homepage"))

#endregion
#---------------------------------------------------------------Run Flask--------------------------------------------------------------------#
if __name__ == '__main__':
    app.run('127.0.0.2','80')