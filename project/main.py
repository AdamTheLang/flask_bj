# main.py

from flask import abort, Blueprint, flash, redirect, render_template, request
from flask_login import login_required, current_user

from . import models, forms, db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/edit_org/<org_id>', methods=['GET', 'POST'])
@main.route('/edit_org/', methods=['GET', 'POST'])
@main.route('/edit_org', methods=['GET', 'POST'])
def edit_org(org_id=None):
    if not current_user.is_authenticated:
        if request.method == 'POST':
            abort(401)
        if org_id is None:
            abort(401)

    org = None
    if org_id:
        org = models.Groups.query.filter_by(id=org_id).first()
        if not org:
            abort(404)
        form = forms.OrganizationEditForm(obj=org)
        formatted_phone = str(form.contact_phone.data)
        if formatted_phone and formatted_phone.isdigit():
            formatted_phone.lstrip('1')
            formatted_phone = (
                "(" + formatted_phone[0:3] + ") " +
                formatted_phone[3:6] + "-" + formatted_phone[6:]
            )
            form.contact_phone.data = formatted_phone

    else:
        form = forms.OrganizationEditForm()

    if form.validate_on_submit():
        if not org:
            org = models.Groups()
        form.populate_obj(org)
        db.session.add(org)
        db.session.commit()
        return redirect('/find_org')

    return render_template('edit_org.html', form=form)


@main.route('/find_org/', methods=['GET'])
@main.route('/find_org', methods=['GET'])
def find_org():
    form = forms.OrganizationSearchForm(request.args)
    query = models.Groups.query
    if form.org_name.data:
        query = query.filter(
            models.Groups.org_name.like('%' + form.org_name.data + '%')
        )
    if form.bj_contact.data:
        query = query.filter(
            models.Groups.bj_contact.like('%' + form.bj_contact.data + '%')
        )
    if form.state.data and form.state.data != 'Any':
        query = query.filter_by(state=form.state.data)
    if form.issue.data and form.issue.data != 'Any':
        query = query.filter(
            models.Groups.issues.any(models.Issues.issue_key == form.issue.data)
        )
    if form.population.data and form.population.data != 'Any':
        query = query.filter(models.Groups.populations.any(
            models.Populations.pop_key == form.population.data
        ))

    results = list(query.order_by(models.Groups.org_name).all())

    return render_template('find_org.html', form=form, results=results)


@main.route('/threats/<threat_id>', methods=['GET', 'POST'])
@main.route('/threats/', methods=['GET', 'POST'])
@main.route('/threats', methods=['GET', 'POST'])
def threats(threat_id=None):
    if not current_user.is_authenticated:
        if request.method == 'POST':
            abort(401)
        if threat_id is None:
            abort(401)

    all_threats = list(
        models.Threats.query.order_by(models.Threats.threat_key).all()
    )
    if threat_id is not None:
        this_threat = [
            threat for threat in all_threats if int(threat.id) == int(threat_id)
        ][0]
        form = forms.ThreatForm(obj=this_threat)
    else:
        this_threat = None
        form = forms.ThreatForm()

    if form.validate_on_submit():
        if this_threat is None:
            threat = models.Threats()
        form.populate_obj(threat)
        db.session.add(threat)
        db.session.commit()
        return redirect('/threats')

    return render_template('threats.html', form=form, all_threats=all_threats)


@main.route('/edit_state/<abbrev>', methods=['GET', 'POST'])
def states(abbrev=None):
    if request.method == 'POST' and not current_user.admin:
        abort(401)

    all_states = list(models.States.query.order_by(models.States.name).all())
    all_abbrevs = [st.abbrev for st in all_states]
    if abbrev not in all_abbrevs:  # catches None too
        abort(404)

    this_state = [s for s in all_states if abbrev == s.abbrev][0]
    form = forms.StateForm(obj=this_state)
    if form.validate_on_submit():
        form.populate_obj(this_state)
        db.session.add(this_state)
        db.session.commit()
        return redirect('/edit_state')

    election_threat_zip = zip(form.election_state_threats,
                              form.election_threat_litigation,
                              form.election_threat_doj,
                              form.election_threat_organizing)
    antivoter_threat_zip = zip(form.antivoter_state_threats,
                               form.antivoter_threat_litigation,
                               form.antivoter_threat_doj,
                               form.antivoter_threat_organizing)

    current_legislation = list(
        models.Legislation.query
        .filter_by(state=abbrev, defunct=0)
        .order_by(models.Legislation.abbrev).all()
    )
    defunct_legislation = list(
        models.Legislation.query
        .filter_by(state=abbrev, defunct=1)
        .order_by(models.Legislation.abbrev).all()
    )

    leg_tl = {
        0: 'Unset',
        1: 'Low',
        5: 'Significant',
        10: 'Hair On Fire'
    }

    return render_template('edit_state.html', form=form, abbrev=abbrev,
                           election_threats=election_threat_zip,
                           antivoter_threats=antivoter_threat_zip,
                           current_legislation=current_legislation,
                           defunct_legislation=defunct_legislation,
                           legislation_threat_lookup=leg_tl)


@main.route('/find_state/', methods=['GET'])
@main.route('/find_state', methods=['GET'])
def find_state():
    form = forms.StateSearchForm(request.args)
    query = models.States.query
    if form.threat_rating.data and form.threat_rating.data != -1:
        query = query.filter_by(threat_rating=form.threat_rating.data)

    results = list(query.order_by(models.States.threat_rating.desc()).all())
    tl = {
        0: 'Unset',
        1: 'Okay For Now',
        5: 'At Risk',
        10: 'Hair On Fire'
    }

    return render_template(
        'find_state.html', form=form, results=results, threat_lookup=tl
    )


@main.route('/edit_leg/<leg_id>', methods=['GET', 'POST'])
@main.route('/edit_leg/', methods=['GET', 'POST'])
@main.route('/edit_leg/', methods=['GET', 'POST'])
def legislation(leg_id=None):
    if not current_user.is_authenticated:
        if request.method == 'POST':
            abort(401)
        if leg_id is None:
            abort(401)

    legislation = None
    if leg_id:
        legislation = models.Legislation.query.filter_by(id=leg_id).first()
        if not legislation:
            abort(404)
        form = forms.LegislationForm(obj=legislation)
    else:
        form = forms.LegislationForm()

    if form.validate_on_submit():
        if not legislation:
            legislation = models.Legislation()
        form.populate_obj(legislation)
        db.session.add(legislation)
        db.session.commit()
        return redirect('/edit_state/' + legislation.state_obj.abbrev + "#legislation")

    return render_template('edit_leg.html', form=form)
