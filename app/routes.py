from flask import render_template, redirect, url_for, flash, request, session, jsonify
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
                return redirect(url_for('influencerProfile'))
            else:
                flash('Invalid username or password', 'danger')
        elif Sponsor.query.filter_by(username=username).first():
            user = Sponsor.query.filter_by(username=username).first()
            if user and (user.password == password):
                flash('Login successful', 'success')
                session['user_id'] = user.id
                return redirect(url_for('sponsorProfile'))
            else:
                flash('Invalid username or password', 'danger')
        else:
            flash('Please Register before logging in', 'danger')

    return render_template('login.html')

@app.route('/admin')
def adminLogin():
    return render_template('loginAdmin.html')

@app.route('/register')
def register():
    return render_template('register.html')

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
    if user_id:
        influencer = Influencer.query.get(user_id)
        if influencer:
            return render_template('influencerProfile.html', influencer=influencer)
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
                accepted=False
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
    if user_id:
        sponsor = Sponsor.query.get(user_id)
        if sponsor:
            requests = Adrequest.query.filter_by(requested_by="influencer", sponsor_id=user_id).all()
            request_empty = len(requests)==0
            return render_template('sponsorProfile.html', sponsor=sponsor, requests=requests, request_empty=request_empty)
    return redirect(url_for('login'))

@app.route('/campaign', methods=['GET', 'POST'])
def sponsorCampaign():
    if request.method == 'POST':
        if 'delete' in request.form:
            campaign_id = request.form.get('campaign_id')
            campaign = Campaign.query.get(campaign_id)
            if campaign:
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
        sponsor_id = session.get('user_id')
        

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if campaign_id:
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
            is_empty = len(campaigns) == 0
            return render_template('sponsorCampaign.html', sponsor=sponsor, campaigns=campaigns, is_empty=is_empty)
    return redirect(url_for('login'))





@app.route('/view_campaigns')
def view_campaigns():
    campaigns = Campaign.query.all()
    return render_template('view_campaign.html', campaigns=campaigns)

