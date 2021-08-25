# models.py

from flask_login import UserMixin
from sqlalchemy.sql import func

from . import db


class Volunteers(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    phone = db.Column(db.BigInteger)


class StateInterests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'),
                             nullable=False)
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'),
                      nullable=False)


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)  # fine if it's blank
    description = db.Column(db.Text)
    team_state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))


class TeamVolunteers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'),
                        nullable=False)
    team_id = db.Column(db.String(2), db.ForeignKey('teams.id'),
                        nullable=False)


class States(db.Model):
    abbrev = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.Text)
    government_desc = db.Column(db.Text)
    leg_period = db.Column(db.Text)
    supreme_court = db.Column(db.Text)
    redistricting = db.Column(db.Text)
    state_teams = db.relationship('Teams', backref='state')


class Legislation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))
    # canonical string for IDing the legislation and associated engagements
    abbrev = db.Column(db.Text)
    desc = db.Column(db.Text)
    leg_type = db.Column(db.Text)
    introduced = db.Column(db.Date)
    status_updated = db.Column(db.Date, nullable=False,
                               server_default="CURRENT_DATE")
    current_status = db.Column(db.Text)
    defunct = db.Column(db.Boolean)
    # Let's just make it 0 to 5 for now and if we start doing this with
    # legislation we support we can use -1 to -5.
    threat_level = db.Column(db.Integer, nullable=False, default=0)
    targets = db.Column(db.Text)
    doj_response = db.Column(db.Text)
    sources = db.Column(db.Text)


class Engagements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'))
    strategy = db.Column(db.Text)
    status = db.Column(db.Text)
    status_updated = db.Column(db.Date, nullable=False,
                               server_default="CURRENT_DATE")
    closed = db.Column(db.Boolean)


class Groups(db.Model):
    org_name = db.Column(db.String(40))
    org_url = db.Column(db.String(200))
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))
    issues = db.Column(db.String(20))
    populations = db.Column(db.String(20))
    actions = db.Column(db.Text)
    bj_contact = db.Column(db.String(40))
    first_contact = db.Column(db.Date)
    latest_contact = db.Column(db.Date)
    followup = db.Column(db.Text)
    notes = db.Column(db.Text)
    contact_name = db.Column(db.Text)
    contact_title = db.Column(db.Text)
    contact_phone = db.Column(db.BigInteger)
    contact_email = db.Column(db.Text)


# class GroupPrimaryIssues(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
#     issue_key = db.Column(db.String(20), db.ForeignKey('issues.issue_key'))
#
#
# class Issues(db.Model):
#     issue_key = db.Column(db.String(20), primary_key=True)
#     issue_name = db.Column(db.Text)


class EngagementGroups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.Integer, db.ForeignKey('groups.id'))
    engagement_id = db.Column(db.Integer, db.ForeignKey('engagements.id'))


class EngagementTeams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    engagement_id = db.Column(db.Integer, db.ForeignKey('engagements.id'))


class Actions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    desc = db.Column(db.Text)
    engagement_id = db.Column(db.Integer, db.ForeignKey('engagements.id'))
    status = db.Column(db.Text)
    status_updated = db.Column(db.Date, nullable=False,
                               server_default="CURRENT_DATE")
    closed = db.Column(db.Boolean)
    # does this need a team id or is it enough that the engagement has one?
    # does this need group ids or is it enough that the engagement has one?
