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
from flask_wtf import FlaskForm

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


STATE_ABBREV = ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                'HI', 'ID', 'IL', 'IN', 'IO', 'KS', 'KY', 'LA', 'ME', 'MD',
                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY')

ISSUES = (
    ('ISSUE_1', 'Issue 1'),
    ('ISSUE_2', 'Issue 2'),
    ('ISSUE_3', 'Issue 3'),
)

POPULATIONS = (
    ('POP_1', 'Population 1'),
    ('POP_2', 'Population 2'),
    ('POP_3', 'Population 3'),
)


def is_phone(form, field):
    digits = ''.join(filter(str.isdigit, field.data))
    if not (1999999999 < int(digits) < 19999999999):
        raise validators.ValidationError("Invalid telephone number.")
    return True


class OrganizationSearchForm(FlaskForm):
    org_name = StringField('Org Name', [validators.Length(min=4, max=40)])

    state = SelectField(
        label='State',
        choices=[('Any', 'Any')] + [(state, state) for state in STATE_ABBREV]
    )

    issue = SelectField(
        label='Primary Issues',
        choices=(('Any', 'Any'),) + ISSUES,
    )

    population = SelectField(
        label='Populations Served',
        choices=(('Any', 'Any'),) + POPULATIONS
    )



class OrganizationEditForm(FlaskForm):
    id = IntegerField()
    org_name = StringField('Org Name', [validators.Length(min=4, max=40)])
    org_url = StringField('Org URL', [validators.Length(max=200)])

    state = SelectField(
        label='State',
        choices=[(state, state) for state in STATE_ABBREV]
    )

    issues = SelectField(
        label='Primary Issues',
        choices=ISSUES,
    )

    populations = SelectField(
        label='Populations Served',
        choices=POPULATIONS
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
        validators=[is_phone]
    )

    contact_email = StringField(
        label='Email Address',
        validators=[validators.Length(max=50), validators.Email(),]
    )
