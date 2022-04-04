from functools import partial
import re

from wtforms.fields import (
    BooleanField,
    DateField,
    IntegerField,
    PasswordField,
    RadioField,
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
from werkzeug.security import check_password_hash

from project import models


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class QueryMultiCheckboxField(QuerySelectMultipleField):
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

    return threats


def _election_threat_query_factory():
    threats = list(models.Threats.query.filter(
        models.Threats.threat_key < 200
    ).order_by(models.Threats.threat_key).all())

    return threats


def _antivoter_threat_query_factory():
    threats = list(models.Threats.query.filter(
        models.Threats.threat_key >= 200
    ).order_by(models.Threats.threat_key).all())

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
            [('Any', 'Any'), ] + [(s.abbrev, s.name) for s in states if s.abbrev]
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
        label='Action Issues',
    )

    population = SelectField(
        label='Populations Served',
    )


def validate_not_empty_state(form, field):
    if field.data.abbrev == '':
        raise validators.ValidationError("You must choose a state, or 'national'.")
    return True


def validate_add_http(https, form, field):
    prefix = 'http://'
    if https:
        prefix = 'https://'
    if not field.data.startswith('http'):
        field.data = prefix + field.data
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
            partial(validate_add_http, False),
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
        label='Action Issues',
        query_factory=_issue_query_factory
    )

    populations = QuerySelectMultipleField(
        label='Populations Served',
        query_factory=_pop_query_factory
    )

    actions = TextAreaField(
        label='Typical Actions',
        validators=[validators.Length(max=5000)]
    )

    organization_notes = TextAreaField(
        label='Organization Notes',
        validators=[validators.Length(max=5000)]
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
        validators=[validators.Length(max=5000)]
    )

    interaction_notes = TextAreaField(
        label='BJ Interaction Notes',
        validators=[validators.Length(max=5000)]
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
        validators=[validators.Length(max=5000)]
    )

    threat_response = TextAreaField(
        label='Threats Responded To',
        validators=[validators.Length(max=5000)]
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
    does = TextAreaField('What It Does', [validators.Length(max=5000)])
    matters = TextAreaField('Why It Matters', [validators.Length(max=5000)])


class StateSearchForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(StateSearchForm, self).__init__(*args, **kwargs)
        states = models.States.query.order_by(models.States.name).all()
        self.state.choices = (
            [('Any', 'Any'), ] + [(s.abbrev, s.name) for s in states]
        )

    state = SelectField(
        label='State',
    )

    threat_rating = SelectField(
        label='Threat Level',
        choices=[
            (-1, 'Any'),
            (0, 'Unset'),
            (1, 'Okay For Now'),
            (5, 'At Risk'),
            (10, 'Hair On Fire')
        ]
    )


class StateForm(FlaskForm):

    name = StringField('State Name', [validators.Length(min=3),
                                      validators.Length(max=25)])
    threat_rating = SelectField(
        label='Threat Level',
        choices=[
            (0, 'Unset'),
            (1, 'Okay For Now'),
            (5, 'At Risk'),
            (10, 'Hair On Fire')
        ]
    )

    republican_strategy = TextAreaField(
        label='Republican Strategy',
        validators=[validators.Length(max=5000)]
    )

    our_strategy = TextAreaField(
        label='Our Strategy',
        validators=[validators.Length(max=5000)]
    )

    state_officials = TextAreaField(
        label='State Elected Officials',
        validators=[validators.Length(max=5000)]
    )

    national_officials = TextAreaField(
        label='US Representatives & Senators',
        validators=[validators.Length(max=5000)]
    )

    lege_desc = TextAreaField(
        label='State Legislature',
        validators=[validators.Length(max=5000)]
    )

    lege_term = TextAreaField(
        label='State Legislative Term',
        validators=[validators.Length(max=5000)]
    )

    supreme_court = TextAreaField(
        label='State Supreme Court',
        validators=[validators.Length(max=5000)]
    )

    redistricting = TextAreaField(
        label='Redistricting Method/Info',
        validators=[validators.Length(max=5000)]
    )

    election_state_threats = QueryMultiCheckboxField(
        label='', query_factory=_election_threat_query_factory
    )

    election_threat_litigation = QueryMultiCheckboxField(
        label='', query_factory=_election_threat_query_factory
    )

    election_threat_doj = QueryMultiCheckboxField(
        label='', query_factory=_election_threat_query_factory
    )

    election_threat_organizing = QueryMultiCheckboxField(
        label='', query_factory=_election_threat_query_factory
    )

    antivoter_state_threats = QueryMultiCheckboxField(
        label='', query_factory=_antivoter_threat_query_factory
    )

    antivoter_threat_litigation = QueryMultiCheckboxField(
        label='', query_factory=_antivoter_threat_query_factory
    )

    antivoter_threat_doj = QueryMultiCheckboxField(
        label='', query_factory=_antivoter_threat_query_factory
    )

    antivoter_threat_organizing = QueryMultiCheckboxField(
        label='', query_factory=_antivoter_threat_query_factory
    )


class LegislationForm(FlaskForm):

    name = StringField('Legislation Name', [validators.Length(min=3),
                                            validators.Length(max=100)])

    state_obj = QuerySelectField(
        label='State',
        query_factory=_state_query_factory,
        validators=[validate_not_empty_state]
    )

    abbrev = StringField('Identifier (e.g. HR-11)', [validators.Length(max=20)])
    desc = TextAreaField('Description/Details', [validators.Length(max=5000)])

    introduced = DateField(
        label='Date Introduced',
        format='%m/%d/%y',
        validators=[validators.Optional()]
    )

    status_updated = DateField(
        label='Status Current As Of',
        format='%m/%d/%y',
        validators=[validators.Optional()]
    )

    current_status = StringField('Current Status', [validators.Length(max=80)])
    defunct = BooleanField('Defunct')

    threat_level = SelectField(
        label='Threat Level',
        choices=[
            (0, 'Unset'),
            (1, 'Low'),
            (5, 'Significant'),
            (10, 'Hair On Fire')
        ]
    )

    targets = TextAreaField(
        label="Legislation Targets and Goals",
        validators=[validators.Length(max=5000)]
    )

    doj_response = TextAreaField(
        label="DOJ Response",
        validators=[validators.Length(max=5000)]
    )

    sources = TextAreaField(
        label="Information Sources",
        validators=[validators.Length(max=5000)]
    )

    election_threats = QueryMultiCheckboxField(
        label='Legislation Election Subversion/Politicization Threats',
        query_factory=_election_threat_query_factory
    )

    antivoter_threats = QueryMultiCheckboxField(
        label='Legislation Anti-Voter/Anti-Voting Threats',
        query_factory=_antivoter_threat_query_factory
    )


def _sm_org_type_query_factory():
    return models.MediaEntityTypes.query.order_by(
        models.MediaEntityTypes.display
    ).all()


def _beat_query_factory():
    return models.MediaBeats.query.order_by(
        models.MediaBeats.display
    ).all()


def validate_add_host(host, form, field):
    assert host
    if not field.data:
        return True

    if '/' not in field.data or '.' not in field.data:
        field.data = field.data.replace('@', '')
        field.data = host + field.data

    return True


def validate_comma_separated(form, field):
    if not field.data:
        return True

    field_list = re.split('; *|, *|[^,;]  *', field.data)
    field.data = ", ".join(field_list)

    return True


def validate_hashes(form, field):
    if not field.data:
        return True

    field_list = field.data.split(', ')
    field_list = [tag if tag.startswith('#') else '#' + tag for tag in field_list]

    field.data = ', '.join(field_list)

    return True


class SocialMediaForm(FlaskForm):

    name = StringField(
        "Social Media Contact Name",
        validators=[validators.length(min=2, max=150)]
    )

    sm_org = StringField(
        "Organization",
        validators=[validators.length(max=150)]
    )

    entity_type_obj = QuerySelectField(
        "Type",
        query_factory=_sm_org_type_query_factory
    )

    state_obj = QuerySelectField(
        label='State',
        query_factory=_state_query_factory,
        validators=[validate_not_empty_state]
    )

    twitter = StringField(
        'Twitter URL',
        [
            validators.Optional(),
            partial(validate_add_host, 'twitter.com/'),
            partial(validate_add_http, True),
            validators.Length(max=200),
            validators.URL(message='Invalid URL')
        ]
    )

    instagram = StringField(
        'Instagram URL',
        [
            validators.Optional(),
            partial(validate_add_host, 'instagram.com/'),
            partial(validate_add_http, True),
            validators.Length(max=200),
            validators.URL(message='Invalid URL')
        ]
    )

    tiktok = StringField(
        'Tiktok URL',
        [
            validators.Optional(),
            partial(validate_add_host, 'tiktok.com/@'),
            partial(validate_add_http, True),
            validators.Length(max=200),
            validators.URL(message='Invalid URL')
        ]
    )

    hashtags = StringField(
        'Hashtags',
        [
            validate_comma_separated,
            validate_hashes,
            validators.Length(max=200)
        ]
    )

    beat_obj = QuerySelectField(
        'Beat',
        query_factory=_beat_query_factory
    )

    contact_notes = TextAreaField(
        'Contact Notes',
        [validators.Length(max=20000)]
    )


class SocialMediaSearchForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(SocialMediaSearchForm, self).__init__(*args, **kwargs)

        states = models.States.query.order_by(models.States.name).all()
        self.state.choices = (
            [('Any', 'Any'), ] + [(s.abbrev, s.name) for s in states if s.abbrev]
        )
        self.state.default = 'Any'

        types = models.MediaEntityTypes.query.order_by(
            models.MediaEntityTypes.display
        ).all()
        self.entity_type.choices = (
            [('Any', 'Any'), ] + [(t.id, t.display) for t in types]
        )
        self.entity_type.default = 'Any'

        beats = models.MediaBeats.query.order_by(models.MediaBeats.display).all()
        self.beat.choices = (
            [('Any', 'Any'), ] + [(b.id, b.display) for b in beats]
        )
        self.beat.default = 'Any'

    name = StringField(
        "Social Media Contact Name",
        validators=[validators.length(min=2, max=150)]
    )

    sm_org = StringField(
        "Organization",
        validators=[validators.length(max=150)]
    )

    entity_type = SelectField('Type')

    state = SelectField('State')

    beat = SelectField('Special Beat')
