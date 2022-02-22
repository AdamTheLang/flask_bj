# models.py

from flask_login import UserMixin

from project import db


state_interests = db.Table(
    'state_interests',
    db.Column('volunteer_id', db.Integer, db.ForeignKey('volunteers.id')),
    db.Column('state', db.String(2), db.ForeignKey('states.abbrev'))
)


class Volunteers(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    bj_nym = db.Column(db.Text)
    phone = db.Column(db.BigInteger)
    states = db.relationship("States", secondary=state_interests)
    admin = db.Column(db.Boolean)


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


state_threats = db.Table(
    'state_threats',
    db.Column('threat_id', db.Integer, db.ForeignKey('threats.id')),
    db.Column('state_key', db.String(2), db.ForeignKey('states.abbrev'))
)


state_litigations = db.Table(
    'state_litigations',
    db.Column('threat_id', db.Integer, db.ForeignKey('threats.id')),
    db.Column('state_key', db.String(2), db.ForeignKey('states.abbrev'))
)


state_dojs = db.Table(
    'state_dojs',
    db.Column('threat_id', db.Integer, db.ForeignKey('threats.id')),
    db.Column('state_key', db.String(2), db.ForeignKey('states.abbrev'))
)


state_threat_orgs = db.Table(
    'state_threat_orgs',
    db.Column('threat_id', db.Integer, db.ForeignKey('threats.id')),
    db.Column('state_key', db.String(2), db.ForeignKey('states.abbrev'))
)


class States(db.Model):
    def __str__(self):
        return self.name

    abbrev = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.Text)
    threat_rating = db.Column(db.Integer)
    republican_strategy = db.Column(db.Text)
    our_strategy = db.Column(db.Text)

    government_desc = db.Column(db.Text)
    lege_desc = db.Column(db.Text)
    lege_term = db.Column(db.Text)
    supreme_court = db.Column(db.Text)
    redistricting = db.Column(db.Text)
    state_officials = db.Column(db.Text)
    national_officials = db.Column(db.Text)

    state_threats = db.relationship("Threats", secondary=state_threats)
    threat_litigation = db.relationship("Threats", secondary=state_litigations)
    threat_doj = db.relationship("Threats", secondary=state_dojs)
    threat_organizing = db.relationship("Threats", secondary=state_threat_orgs)

    @property
    def election_state_threats(self):
        return [t for t in self.state_threats if int(t.threat_key) < 200]

    @election_state_threats.setter
    def election_state_threats(self, threats):
        assert all(int(t.threat_key) < 200 for t in threats)
        self.state_threats = self.antivoter_state_threats + threats

    @property
    def election_threat_litigation(self):
        return [t for t in self.threat_litigation if int(t.threat_key) < 200]

    @election_threat_litigation.setter
    def election_threat_litigation(self, threats):
        assert all(int(t.threat_key) < 200 for t in threats)
        self.threat_litigation = self.antivoter_threat_litigation + threats

    @property
    def election_threat_doj(self):
        return [t for t in self.threat_doj if int(t.threat_key) < 200]

    @election_threat_doj.setter
    def election_threat_doj(self, threats):
        assert all(int(t.threat_key) < 200 for t in threats)
        self.threat_doj = self.antivoter_threat_doj + threats

    @property
    def election_threat_organizing(self):
        return [t for t in self.threat_organizing if int(t.threat_key) < 200]

    @election_threat_organizing.setter
    def election_threat_organizing(self, threats):
        assert all(int(t.threat_key) < 200 for t in threats)
        self.threat_organizing = self.antivoter_state_threats + threats

    @property
    def antivoter_state_threats(self):
        return [t for t in self.state_threats if int(t.threat_key) >= 200]

    @antivoter_state_threats.setter
    def antivoter_state_threats(self, threats):
        assert all(int(t.threat_key) >= 200 for t in threats)
        self.state_threats = self.election_state_threats + threats

    @property
    def antivoter_threat_litigation(self):
        return [t for t in self.threat_litigation if int(t.threat_key) >= 200]

    @antivoter_threat_litigation.setter
    def antivoter_threat_litigation(self, threats):
        assert all(int(t.threat_key) >= 200 for t in threats)
        self.threat_litigation = self.election_threat_litigation + threats

    @property
    def antivoter_threat_doj(self):
        return [t for t in self.threat_doj if int(t.threat_key) >= 200]

    @antivoter_threat_doj.setter
    def antivoter_threat_doj(self, threats):
        assert all(int(t.threat_key) >= 200 for t in threats)
        self.threat_doj = self.election_threat_doj + threats

    @property
    def antivoter_threat_organizing(self):
        return [t for t in self.threat_organizing if int(t.threat_key) >= 200]

    @antivoter_threat_organizing.setter
    def antivoter_threat_organizing(self, threats):
        assert all(int(t.threat_key) >= 200 for t in threats)
        self.threat_organizing = self.election_threat_organizing + threats


legislation_threats = db.Table(
    'legislation_threats',
    db.Column('legislation_id', db.Integer, db.ForeignKey('legislation.id')),
    db.Column('threat_id', db.Integer, db.ForeignKey('threats.id'))
)


group_legislation = db.Table(
    'group_legislation',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('legislation_id', db.Integer, db.ForeignKey('legislation.id'))
)


class Legislation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))
    state_obj = db.relationship("States")

    # canonical string for IDing the legislation and associated engagements
    abbrev = db.Column(db.Text)
    desc = db.Column(db.Text)
    leg_type = db.Column(db.Text)
    introduced = db.Column(db.Date)
    status_updated = db.Column(db.Date)
    current_status = db.Column(db.Text)
    defunct = db.Column(db.Boolean)

    threat_level = db.Column(db.Integer, nullable=False, default=0)
    targets = db.Column(db.Text)
    doj_response = db.Column(db.Text)
    sources = db.Column(db.Text)

    threats =  db.relationship("Threats", secondary=legislation_threats)
    groups = db.relationship("Groups", secondary=group_legislation, viewonly=True)

    @property
    def antivoter_threats(self):
        return [t for t in self.threats if int(t.threat_key) >= 200]

    @antivoter_threats.setter
    def antivoter_threats(self, threats):
        assert all(int(t.threat_key) >= 200 for t in threats)
        self.threats = self.election_threats + threats

    @property
    def election_threats(self):
        return [t for t in self.threats if int(t.threat_key) < 200]

    @election_threats.setter
    def election_threats(self, threats):
        assert all(int(t.threat_key) < 200 for t in threats)
        self.threats = self.antivoter_threats + threats

#
# group_litigation = db.Table(
#     'group_litigation',
#     db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
#     db.Column('litigation_id', db.Integer, db.ForeignKey('litigation.id'))
# )
#
#
# legislation_litigation = db.Table(
#     'legislation_litigation',
#     db.Column('litigation_id', db.Integer, db.ForeignKey('litigation.id')),
#     db.Column('legislation_id', db.Integer, db.ForeignKey('legislation.id'))
# )
#
#
# class Litigation(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Text)
#     notes = db.Column(db.Text)
#
#     state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))
#     state_obj = db.relationship("States")
#
#     groups = db.relationship("Groups", secondary=group_litigation, viewonly=True)
#     threats =  db.relationship("Threats", secondary=legislation_threats)
#
#     @property
#     def antivoter_threats(self):
#         return [t for t in self.threats if int(t.threat_key) >= 200]
#
#     @antivoter_threats.setter
#     def antivoter_threats(self, threats):
#         assert all(int(t.threat_key) >= 200 for t in threats)
#         self.threats = self.election_threats + threats
#
#     @property
#     def election_threats(self):
#         return [t for t in self.threats if int(t.threat_key) < 200]
#
#     @election_threats.setter
#     def election_threats(self, threats):
#         assert all(int(t.threat_key) < 200 for t in threats)
#         self.threats = self.antivoter_threats + threats


class Engagements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))
    legislation_id = db.Column(db.Integer, db.ForeignKey('legislation.id'))
    strategy = db.Column(db.Text)
    status = db.Column(db.Text)
    status_updated = db.Column(db.Date, nullable=False)
    closed = db.Column(db.Boolean)


group_issues = db.Table(
    'group_issues',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('issue_key', db.String(20), db.ForeignKey('issues.issue_key'))
)


group_populations = db.Table(
    'group_populations',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('pop_key', db.String(20), db.ForeignKey('populations.pop_key'))
)


class Groups(db.Model):
    def __str__(self):
        return self.org_name

    id = db.Column(db.Integer, primary_key=True)

    org_name = db.Column(db.String(40))
    org_url = db.Column(db.String(200))
    social_media_url = db.Column(db.String(200))
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))
    state_obj = db.relationship("States")

    issues = db.relationship("Issues", secondary=group_issues)
    populations = db.relationship("Populations", secondary=group_populations)
    legislation = db.relationship("Legislation", secondary=group_legislation)

    actions = db.Column(db.Text)
    bj_contact = db.Column(db.String(40))
    first_contact = db.Column(db.Date)
    latest_contact = db.Column(db.Date)
    followup = db.Column(db.Text)
    organization_notes = db.Column(db.Text)
    threat_response = db.Column(db.Text)

    interaction_notes = db.Column(db.Text)

    contact_name = db.Column(db.Text)
    contact_title = db.Column(db.Text)
    contact_phone = db.Column(db.BigInteger)
    contact_email = db.Column(db.Text)
    contact_notes = db.Column(db.Text)

    to_delete = db.Column(db.Boolean)


class Issues(db.Model):
    def __str__(self):
        return self.issue_name

    issue_key = db.Column(db.String(20), primary_key=True)
    issue_name = db.Column(db.Text)


class Populations(db.Model):
    def __str__(self):
        return self.pop_name

    pop_key = db.Column(db.String(20), primary_key=True)
    pop_name = db.Column(db.Text)


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
    group = db.Column(db.Integer, db.ForeignKey('groups.id'))
    state = db.Column(db.String(2), db.ForeignKey('states.abbrev'))

    desc = db.Column(db.Text)
    engagement_id = db.Column(db.Integer, db.ForeignKey('engagements.id'))
    status = db.Column(db.Text)
    status_updated = db.Column(db.Date)
    closed = db.Column(db.Boolean)
    # does this need a team id or is it enough that the engagement has one?
    # does this need group ids or is it enough that the engagement has one?


class Threats(db.Model):
    def __str__(self):
        return self.name

    id = db.Column(db.Integer, primary_key=True)
    threat_key = db.Column(db.Integer)
    name = db.Column(db.Text)
    source = db.Column(db.Text)
    does = db.Column(db.Text)
    matters = db.Column(db.Text)

# class SocialMediaEntity(db.Model):
#     def _str_(self):
#         return self.name
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Text)
#     entity_type = db.Column(db.Integer)
#     sm_org = db.Column(db.Text)
#     org_type = db.Column(db.Integer)
#


