from flask import render_template,render_template_string, redirect, url_for, flash, request, session, jsonify
from app import app, db
from app.models import Influencer, Sponsor, Campaign, Adrequest
from datetime import datetime

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = None
        if Influencer.query.filter_by(username=username).first():
            user = Influencer.query.filter_by(username=username).first()
            if user and (user.password == password):
                flash('Login successful', 'success')
                session['user_id'] = user.id
                if not user.flag:
                    return redirect(url_for('influencerProfile'))
                else:
                    return render_template_string('<h1>You have been flagged by the Admin</h1>')
            else:
                flash('Invalid username or password', 'danger')
        elif Sponsor.query.filter_by(username=username).first():
            user = Sponsor.query.filter_by(username=username).first()
            if user and (user.password == password):
                flash('Login successful', 'success')
                session['user_id'] = user.id
                if not user.flag:
                    return redirect(url_for('sponsorProfile'))
                else:
                    return render_template_string('<h1>You have been flagged by the Admin</h1>')
            else:
                flash('Invalid username or password', 'danger')
        else:
            flash('Please Register before logging in', 'danger')

    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/toggle-flag', methods=['POST'])
def toggle_flag():
    entity_type = request.form.get('entity_type')
    entity_id = request.form.get('entity_id')

    if entity_type == 'influencer':
        user = Influencer.query.get(entity_id)
    elif entity_type == 'sponsor':
        user = Sponsor.query.get(entity_id)
    
    if user:
        user.flag = not user.flag  # Toggle the flag status
        db.session.commit()
    
    return redirect(url_for('adminFind'))


# -------------------------------INFLUENCER-----------------------------------------

@app.route('/register-influencer', methods=['GET', 'POST'])
def registerInfluencer():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        platform = request.form.get('platform')

        new_user = Influencer(fname=fname, lname=lname, phone=phone, username=username, password=password, platform=platform)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    
    return render_template('registerInf.html')


@app.route('/influencer-profile')
def influencerProfile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    influencer = Influencer.query.get(user_id)
    if influencer:
        actives = Adrequest.query.filter_by(influencer_id=user_id, status='accepted').all()
        active_empty = len(actives) == 0
        return render_template('influencerProfile.html', influencer=influencer, actives=actives, active_empty=active_empty)
    return redirect(url_for('login'))

@app.route('/influencer-find', methods=['GET', 'POST'])
def influencerFind():
    if request.method == 'POST':
        campaign_id = request.form.get('campaign_id')
        sponsor_id = request.form.get('sponsor_id')
        influencer_id = session.get('user_id')
        message = request.form.get('message')
        requirements = request.form.get('requirements')
        payment_amount = float(request.form.get('payment_amount'))

        new_request = Adrequest(
                campaign_id=campaign_id,
                influencer_id=influencer_id,
                sponsor_id=sponsor_id,
                message=message,
                requirements=requirements,
                payment_amount=payment_amount,
                requested_by='influencer',
                sent=True,
                status='pending'
        )
        flash('Request Sent Successfully', 'success')
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('influencerFind'))

    return render_template('influencerFind.html', campaigns=Campaign.query.join(Sponsor).all())


# -------------------------------------SPONSOR---------------------------------------------

@app.route('/register-sponsor', methods=['GET', 'POST'])
def registerSponsor():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        password = request.form.get('password')
        industry = request.form.get('industry')

        new_user = Sponsor(fname=fname, lname=lname, username=username, password=password, industry=industry)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('login'))

    return render_template('registerSpo.html')

@app.route('/sponsor-profile', methods=['GET', 'POST'])
def sponsorProfile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        request_id = request.form.get('request_id')
        ad_request = Adrequest.query.get(request_id)

        if ad_request:
            if action == 'accept':
                ad_request.status = 'accepted'
                db.session.commit()
                flash('Request accepted successfully', 'success')
            elif action == 'reject':
                db.session.delete(ad_request)
                db.session.commit()
                flash('Request rejected successfully', 'success')

        return redirect(url_for('sponsorProfile'))

    sponsor = Sponsor.query.get(user_id)
    if sponsor:
        requests = Adrequest.query.filter_by(requested_by="influencer", sponsor_id=user_id, status='pending').all()
        actives = Adrequest.query.filter_by(sponsor_id=user_id, status='accepted').all()
        request_empty = len(requests) == 0
        active_empty = len(actives) == 0
        return render_template('sponsorProfile.html', sponsor=sponsor, requests=requests, request_empty=request_empty, actives=actives, active_empty=active_empty)
    
    return redirect(url_for('login'))


@app.route('/campaign', methods=['GET', 'POST'])
def sponsorCampaign():
    if request.method == 'POST':
        if 'delete' in request.form:
            campaign_id = request.form.get('campaign_id')
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                Adrequest.query.filter_by(campaign_id=campaign_id).delete()
                db.session.delete(campaign)
                db.session.commit()
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Campaign not found'}), 404
            
        campaign_id = request.form.get('campaign_id')
        title = request.form.get('title')
        description = request.form.get('description')
        niche = request.form.get('niche')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        budget = float(request.form.get('budget'))
        visibility = request.form.get('visibility')
        message = request.form.get('message')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')
        influencer_id = request.form.get('influencer_id')
        sponsor_id = session.get('user_id')
        

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if request.form.get('request'):
            new_adrequest = Adrequest(
                campaign_id=campaign_id,
                message=message,
                requirements=requirements,
                payment_amount=payment_amount,
                influencer_id=influencer_id,
                status='pending'
            )
            db.session.add(new_adrequest)
            db.session.commit()
            return jsonify({'status': 'success'})

        elif campaign_id:
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                campaign.title = title
                campaign.description = description
                campaign.niche = niche
                campaign.start_date = start_date
                campaign.end_date = end_date
                campaign.budget = budget
                campaign.visibility = visibility
                campaign.sponsor_id = sponsor_id
                db.session.commit()

        else:  # Add new campaign
            new_campaign = Campaign(title=title, description=description, niche=niche, start_date=start_date, end_date=end_date, budget=budget, visibility=visibility, sponsor_id=sponsor_id)
            db.session.add(new_campaign)
            db.session.commit()
        return redirect(url_for('sponsorCampaign'))
    
    user_id = session.get('user_id')
    if user_id:
        sponsor = Sponsor.query.get(user_id)
        if sponsor:
            campaigns = Campaign.query.filter_by(sponsor_id=user_id).all()
            influencers = Influencer.query.all()
            is_empty = len(campaigns) == 0
            return render_template('sponsorCampaign.html', sponsor=sponsor, campaigns=campaigns, is_empty=is_empty, influencers=influencers)
    return redirect(url_for('login'))

@app.route('/sponsor-find', methods=['GET', 'POST'])
def sponsorFind():
    influencers = Influencer.query.all()
    return render_template('sponsorFind.html', influencers=influencers)


# -------------------------------------ADMIN--------------------------------------------

@app.route('/admin',  methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':
        username = request.form.get('adminUser')
        password = request.form.get('adminPassword')
        if username == 'admin' and password == 'abc123':
            return redirect(url_for('adminProfile'))
    return render_template('loginAdmin.html')

@app.route('/admin-profile', methods=['GET', 'POST'])
def adminProfile():
    ongoings = Adrequest.query.filter_by(status='accepted').all()
    return render_template('adminProfile.html', ongoings=ongoings)

@app.route('/admin-find', methods=['GET', 'POST'])
def adminFind():
    campaigns = Campaign.query.all()
    influencers = Influencer.query.all()
    sponsors = Sponsor.query.all()

    if request.method == 'POST':
        entity_type = request.form.get('entity_type')
        entity_id = request.form.get('entity_id')

        if entity_type == 'influencer':
            influencer = Influencer.query.get(entity_id)
            if influencer:
                influencer.flag = True
                db.session.commit()
                flash('Influencer flagged successfully', 'success')
        elif entity_type == 'sponsor':
            sponsor = Sponsor.query.get(entity_id)
            if sponsor:
                sponsor.flag = True
                db.session.commit()
                flash('Sponsor flagged successfully', 'success')
        
        return redirect(url_for('adminFind'))

    return render_template('adminFind.html', campaigns=campaigns, influencers=influencers, sponsors=sponsors)


@app.route('/logout-admin')
def adminLogout():
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('adminLogin'))


# ----------------------------------------COMMON-------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


# -----------------------------------TESTING-----------------------------------------------------

@app.route('/view_campaigns')
def view_campaigns():
    campaigns = Campaign.query.all()
    return render_template('view_campaign.html', campaigns=campaigns)

