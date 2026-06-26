from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

@main_bp.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", user=session.get("user"))

@main_bp.route("/diagnostic")
def diagnostic():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template("diagnostic.html", user=session.get("user"))

@main_bp.route('/profile/update', methods=['GET','POST'])
def profile_update():
    from flask import request, flash, redirect, url_for
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        fields = ['first_name','last_name','email','phone',
                  'car_brand','car_model','car_year','mileage',
                  'fuel_type','transmission']
        try:
            from app.utils.db import execute, fetch_one
            params = [request.form.get(f,'') for f in fields]
            params.append(user['id'])
            execute(
                "UPDATE users SET first_name=%s,last_name=%s,email=%s,phone=%s,"
                "car_brand=%s,car_model=%s,car_year=%s,mileage=%s,"
                "fuel_type=%s,transmission=%s WHERE id=%s",
                params
            )
            updated = fetch_one("SELECT * FROM users WHERE id=%s",(user['id'],))
            if updated:
                session['user'] = dict(updated)
                session.modified = True
            flash('Profile updated successfully!','success')
        except Exception as e:
            flash(f'Update failed: {e}','error')
        return redirect(url_for('main.profile_update'))
    from flask import render_template
    return render_template('profile_update.html', user=user)


@main_bp.route('/obd')
def obd_page():
    from flask import render_template
    user = session.get('user') or {}
    return render_template('obd.html', user=user)

@main_bp.route('/payment')
def payment():
    from flask import render_template, request
    user = session.get('user') or {}
    plan_name  = request.args.get('plan', 'Pro')
    plan_price = '590' if plan_name.lower() == 'pro' else '990'
    return render_template('payment.html',
                           user=user,
                           plan_name=plan_name,
                           plan_price=plan_price)


@main_bp.route('/payment/confirm', methods=['POST'])
def payment_confirm():
    from flask import request, jsonify
    data   = request.get_json(silent=True) or {}
    method = data.get('method','baridmob')
    plan   = data.get('plan','pro')
    user   = session.get('user') or {}

    # Mark subscription in session
    session['subscribed']      = True
    session['subscription_plan']= plan
    session.modified = True

    # Save to DB
    try:
        from app.utils.db import execute
        if user.get('id'):
            execute(
                'INSERT INTO diagnostics(user_id,input_text,top_fault) VALUES(%s,%s,%s)',
                (user['id'], f'SUBSCRIPTION:{plan}', f'Payment via {method}')
            )
    except Exception:
        pass

    return jsonify({'success': True, 'plan': plan,
                    'message': f'Subscription activated: {plan}'})
