from app import app, db
from app.mock_door import await_knock, open_door, reject_knock
from app.forms import LoginForm, RegistrationForm
from app.models import Call, User
from app.camera import VideoCamera
from flask import flash, redirect, render_template, request, Response, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')

@app.route('/camera')
@login_required
def show_door():
    return render_template("camera.html", title="Hello, it's me")

@app.route('/action', methods=['POST'])
@login_required
def action():
    if request.form.get('open'):
        open_door()
        call = Call(open=True, user_id=current_user.get_id())
    elif request.form.get('reject'):
        reject_knock()
        call = Call(open=False, user_id=current_user.get_id())
    db.session.add(call)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/calls')
@login_required
def calls():
    calls = Call.query.all()
    return render_template("calls.html", title='List of calls', calls=calls)

@app.route('/poll')
def sse():
    def eventKnock():
        while True:
            await_knock()
            yield "data:knock\n\n"
    return Response(eventKnock(), mimetype="text/event-stream")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have registered a new user!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video')
@login_required
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
