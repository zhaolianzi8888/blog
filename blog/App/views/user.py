from flask import Blueprint,render_template,flash,redirect,url_for
from App.forms import Register,AgainActivate,Login #导入注册表单类
from App.models import User #导入User模型类
from App.email import send_mail
from flask_login import login_required,logout_user,login_user,current_user
from datetime import datetime
from App.extensions import cache


user = Blueprint('user',__name__)


#注册
@user.route('/register/',methods=['GET','POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        u = User(username=form.username.data,password=form.userpass.data,email=form.email.data)
        u.save()
        token = u.generate_token() #生成token值
        send_mail('账户激活',u.email,'activate',username=u.username,endpoint='user.activate',token=token)
        flash('恭喜注册成功 请前去邮箱进行激活')
        return redirect(url_for('user.login'))
    return render_template('user/register.html',form=form)





#登录
@user.route('/login/',methods=['GET','POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if not u.check_password(form.userpass.data):
            flash('请输入正确的密码')
        elif not u.confirm:
            flash('该账户还没有激活 请激活后再次登录')
        else:
            u.lastLogin = datetime.utcnow()
            u.save()
            flash('登录成功！！！')
            login_user(u,remember=form.remember.data)
            return redirect(url_for('main.index'))
    return render_template('user/login.html',form=form)


#退出登录
@user.route('/logout/')
def logout():
    flash('退出成功')
    logout_user()
    cache.clear()
    return redirect(url_for('main.index'))

#必须登录才能访问
@user.route('/test/')
@login_required
def test():
    return 'test'