from wtforms.fields import (
    BooleanField,
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms import validators, widgets
from wtforms.ext.sqlalchemy.fields import (
    QuerySelectField,
    QuerySelectMultipleField
)
from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash

from project import models


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def validate_is_phone(form, field):
    phone_int = int(''.join(filter(str.isdigit, field.data)))
    if not (1999999999 < phone_int < 19999999999):
        raise validators.ValidationError("Invalid telephone number.")
    field.data = phone_int
    return True


def validate_old_password_field(form, field):
    if field.data:
        if check_password_hash(current_user.password, field.data):
            print(current_user.password, field.data)
            return True
        raise validators.ValidationError("Incorrect existing password.")
    if form.new_password.data and form.confirm.data == form.new_password.data:
        raise validators.ValidationError("Existing password required to change password.")
    if form.email.data and form.email.data != current_user.email:
        raise validators.ValidationError("Existing password required to change email.")
    return True


def _state_query_factory():
    return models.States.query.order_by(models.States.name).all()


def _state_query_factory_just_states():
    return (
        models.States.query.filter(models.States.abbrev.not_in(['US', '']))
        .order_by(models.States.name).all()
    )


def _nameless_threat_query_factory():
    threats = list(models.Threats.query.order_by(models.Threats.threat_key).all())
    for nt in threats:
        nt.__str__ = lambda x: " "
        nt.__repr__ = lambda x: " "
    print('_nameless_threat_query_factory: %s' % (len(threats),))
    return threats


def _election_threat_query_factory():
    threats = list(models.Threats.query.filter(
        models.Threats.threat_key < 200
    ).order_by(models.Threats.threat_key).all())
    print('_election_threat_query_factory: %s' % (len(threats),))

    return threats


def _antivoter_threat_query_factory():
    threats = list(models.Threats.query.filter(
        models.Threats.threat_key >= 200
    ).order_by(models.Threats.threat_key).all())
    print('_antivoter_threat_query_factory: %s' % (len(threats),))

    return threats


class ProfileForm(FlaskForm):
    name = StringField('Name', [
        validators.Optional(),
        validators.Length(min=4, max=40)
    ])

    bj_nym = StringField("Balloon Juice Nym", [
        validators.Optional(),
        validators.Length(min=4, max=40)
    ])

    email = StringField('Email Address', [
        validators.Optional(),
        validators.Length(min=6, max=35),
        validators.Email(),
    ])
#     phone =  = StringField(
#         label='Contact Phone (Optional)',
#         validators=[validators.Optional(), validate_is_phone]
#     )

    states = QuerySelectMultipleField(
        label='States of Interest',
        query_factory=_state_query_factory_just_states
    )


    old_password = PasswordField('Old Password', [
        validate_old_password_field
    ])

    new_password = PasswordField('New Password', [
        validators.EqualTo('confirm', message='Passwords must match'),
    ])

    confirm = PasswordField('Repeat New Password', [validators.Optional()])


class OrganizationSearchForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationSearchForm, self).__init__(*args, **kwargs)
        states = models.States.query.order_by(models.States.name).all()
        self.state.choices = (
            [('Any', 'Any'), ] + [(s.abbrev, s.name) for s in states]
        )

        issues = models.Issues.query.order_by(models.Issues.issue_name).all()
        self.issue.choices = (
            [('Any', 'Any'), ] + [(i.issue_key, i.issue_name) for i in issues]
        )

        pops = models.Populations.query.order_by(
            models.Populations.pop_name
        ).all()
        self.population.choices = (
            [('Any', 'Any'), ] + [(p.pop_key, p.pop_name) for p in pops]
        )

    org_name = StringField('Organization Name')
    bj_contact = StringField('Balloon Juice Contact')

    state = SelectField(
        label='State',
    )

    issue = SelectField(
        label='Primary Issues',
    )

    population = SelectField(
        label='Populations Served',
    )


def validate_not_empty_state(form, field):
    if field.data.abbrev == '':
        raise validators.ValidationError("You must choose a state, or 'national'.")
    return True


def validate_add_http(form, field):
    if not field.data.startswith('http'):
        field.data = "http://" + field.data
    return True


def _issue_query_factory():
    return models.Issues.query.order_by(models.Issues.issue_name).all()


def _pop_query_factory():
    return models.Populations.query.order_by(models.Populations.pop_name).all()


class OrganizationEditForm(FlaskForm):

    id = IntegerField()
    org_name = StringField('Organization Name', [validators.Length(min=4, max=40)])
    to_delete = BooleanField('Mark for Deletion')
    org_url = StringField(
        'Organization URL',
        [
            validators.Optional(),
            validate_add_http,
            validators.Length(max=200),
            validators.URL(message='Invalid URL')
        ]
    )

    social_media_url = StringField(
        'Social Media URL',
        [
            validators.Optional(),
            validators.Length(max=200),
            validators.URL(message='Invalid URL')
        ]
    )

    state_obj = QuerySelectField(
        label='State',
        query_factory=_state_query_factory,
        validators=[validate_not_empty_state]
    )

    issues = QuerySelectMultipleField(
        label='Primary Issues',
        query_factory=_issue_query_factory
    )

    populations = QuerySelectMultipleField(
        label='Populations Served',
        query_factory=_pop_query_factory
    )

    actions = TextAreaField(
        label='Typical Actions',
        validators=[validators.Length(max=1200)]
    )

    organization_notes = TextAreaField(
        label = 'Organization Notes',
        validators=[validators.Length(max=1200)]
    )

    bj_contact = StringField(
        label='BJ Contact for Call',
        validators=[validators.Length(max=40)]
    )

    first_contact = DateField(
        label='First Contact Date',
        format='%m/%d/%y',
        validators=[validators.Optional()]
    )

    latest_contact = DateField(
        label='Latest Contact Date',
        format='%m/%d/%y',
        validators=[validators.Optional()]
    )

    followup = TextAreaField(
        label='Followup Actions',
        validators=[validators.Length(max=1200)]
    )

    interaction_notes = TextAreaField(
        label='BJ Interaction Notes',
        validators=[validators.Length(max=1200)]
    )

    contact_name = StringField(
        label='Contact Name',
        validators=[validators.Length(max=200)]
    )

    contact_title = StringField(
        label='Contact Title',
        validators=[validators.Length(max=200)]
    )

    contact_phone = StringField(
        label='Contact Phone',
        validators=[validators.Optional(), validate_is_phone]
    )

    contact_email = StringField(
        label='Contact Email Address',
        validators=[
            validators.Optional(),
            validators.Length(max=50),
            validators.Email(),
        ]
    )

    contact_notes = TextAreaField(
        label='Contact Notes',
        validators=[validators.Length(max=1200)]
    )

    threat_response = TextAreaField(
        label='Responding to Primary Threats',
        validators=[validators.Length(max=1200)]
    )


class ThreatForm(FlaskForm):

    threat_key = StringField(
        'Threat ID',
        [validators.Length(min=2), validators.Length(max=20)]
    )

    name = StringField(
        'Threat Name',
        [validators.Length(min=2), validators.Length(max=20)]
    )

    source = StringField('Source', [validators.Length(max=200)])
    does = TextAreaField('What It Does', [validators.Length(max=1200)])
    matters = TextAreaField('Why It Matters', [validators.Length(max=1200)])


class StateForm(FlaskForm):

    name = StringField('State Name', [validators.Length(min=3),
                                      validators.Length(max=25)])
    threat_rating = SelectField(
        label='Threat Level', choices=[(x, str(x)) for x in range(1, 11)]
    )

    republican_strategy = TextAreaField(
        label='Republican Strategy',
        validators=[validators.Length(max=1200)]
    )

    our_strategy = TextAreaField(
        label='Our Strategy',
        validators=[validators.Length(max=1200)]
    )

    state_officials = TextAreaField(
        label='State Elected Officials',
        validators=[validators.Length(max=1200)]
    )

    national_officials = TextAreaField(
        label='US Representatives & Senators',
        validators=[validators.Length(max=1200)]
    )

    lege_desc = TextAreaField(
        label='State Legislature',
        validators=[validators.Length(max=1200)]
    )

    lege_term = TextAreaField(
        label='State Legislative Term',
        validators=[validators.Length(max=1200)]
    )

    supreme_court = TextAreaField(
        label='State Supreme Court',
        validators=[validators.Length(max=1200)]
    )

    redistricting = TextAreaField(
        label='Redistricting Method/Info',
        validators=[validators.Length(max=2000)]
    )

    election_state_threats = MultiCheckboxField(
        label='', choices=[], coerce=int
    )

    election_threat_litigation = MultiCheckboxField(
        label='', choices=[], coerce=int
    )

    election_threat_doj = MultiCheckboxField(
        label='', choices=[], coerce=int
    )

    election_threat_organizing = MultiCheckboxField(
        label='', choices=[], coerce=int
    )

    antivoter_state_threats = MultiCheckboxField(
        label='', choices=[], coerce=int
    )

    antivoter_threat_litigation = MultiCheckboxField(
        label='', choices=[], coerce=int
    )

    antivoter_threat_doj = MultiCheckboxField(
        label='', choices=[], coerce=int
    )

    antivoter_threat_organizing = MultiCheckboxField(
        label='', choices=[], coerce=int
    )
