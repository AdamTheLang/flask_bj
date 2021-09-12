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
from wtforms import validators
from wtforms.ext.sqlalchemy.fields import (
    QuerySelectField,
    QuerySelectMultipleField
)
from flask_wtf import FlaskForm

from project import models

class ProfileForm(FlaskForm):
    username = StringField('Name', [validators.Length(min=4, max=40)])
    email = StringField('Email Address', [
        validators.Length(min=6, max=35),
        validators.Email(),
        validators.DataRequired()
    ])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


def is_phone(form, field):
    digits = ''.join(filter(str.isdigit, field.data))
    if not (1999999999 < int(digits) < 19999999999):
        raise validators.ValidationError("Invalid telephone number.")
    return True


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

    org_name = StringField('Org Name')

    state = SelectField(
        label='State',
    )

    issue = SelectField(
        label='Primary Issues',
    )

    population = SelectField(
        label='Populations Served',
    )


def _state_query_factory():
    return models.States.query.order_by(models.States.name).all()


def _issue_query_factory():
    return models.Issues.query.order_by(models.Issues.issue_name).all()


def _pop_query_factory():
    return models.Populations.query.order_by(models.Populations.pop_name).all()


class OrganizationEditForm(FlaskForm):

    id = IntegerField()
    org_name = StringField('Org Name', [validators.Length(min=4, max=40)])
    org_url = StringField(
        'Org URL',
        [
            validators.Optional(),
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
        query_factory=_state_query_factory
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
        validators=[validators.Length(max=1200)],
    )

    bj_contact = StringField(
        label='BJ Contact for Call',
        validators=[validators.Length(max=40)]
    )

    first_contact = DateField(
        label='First Contacted'
    )

    latest_contact = DateField(
        label='Latest Contact'
    )

    followup = TextAreaField(
        label='Followup Actions',
        validators=[validators.Length(max=1200)]
    )

    notes = TextAreaField(
        label='Other Notes',
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
        validators=[validators.Optional(), is_phone]
    )

    contact_email = StringField(
        label='Email Address',
        validators=[
            validators.Optional(),
            validators.Length(max=50),
            validators.Email(),
        ]
    )
