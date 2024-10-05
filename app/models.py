from app import db

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    platform = db.Column(db.String(20), nullable=False)
    flag = db.Column(db.Boolean, default=False)

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    industry = db.Column(db.String(30), nullable=False)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    flag = db.Column(db.Boolean, default=False)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(50), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    flag = db.Column(db.Boolean, default=False)

class Adrequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    message = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    requested_by = db.Column(db.String(20), nullable=False)
    sent = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    campaign = db.relationship('Campaign', backref='adrequest', lazy=True)
    influencer = db.relationship('Influencer', backref='adrequest', lazy=True)
    sponsor = db.relationship('Sponsor', backref='adrequest', lazy=True)
