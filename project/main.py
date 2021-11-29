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
@login_required
def edit_org(org_id=None):
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
@login_required
def find_org():
    form = forms.OrganizationSearchForm(request.args)
    print(form.state.data)
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
@login_required
def threats(threat_id=None):
    if not current_user.admin:
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
@main.route('/edit_state/', methods=['GET'])
@main.route('/edit_state', methods=['GET'])
@login_required
def states(abbrev=None):
    if request.method == 'POST' and not current_user.admin:
        abort(401)

    all_states = list(models.States.query.order_by(models.States.name).all())
    all_abbrevs = [st.abbrev for st in all_states]
    if abbrev is not None and abbrev not in all_abbrevs:
        abort(404)

    if request.method == 'POST' and abbrev is None:
        abort(404)

    if abbrev is None:
        form = forms.StateForm()
        return render_template('edit_state.html', form=form, abbrev=abbrev)

    this_state = [s for s in all_states if abbrev == s.abbrev][0]
    form = forms.StateForm(obj=this_state)
    threat_objs = models.Threats.query.order_by(models.Threats.threat_key).all()
    election_threats = [(t.id, '') for t in threat_objs if int(t.threat_key) < 200]
    antivoter_threats = [(t.id, '') for t in threat_objs if int(t.threat_key) > 199]
    labeled_election_threats = [(t.id, '\xa0' * 20 + t.name) for t in threat_objs if int(t.threat_key) < 200]
    labeled_antivoter_threats = [(t.id, '\xa0' * 20 + t.name) for t in threat_objs if int(t.threat_key) > 199]

    form.election_state_threats.choices = election_threats
    form.election_threat_litigation.choices = election_threats
    form.election_threat_doj.choices = election_threats
    form.election_threat_organizing.choices = labeled_election_threats

    form.antivoter_state_threats.choices = antivoter_threats
    form.antivoter_threat_litigation.choices = antivoter_threats
    form.antivoter_threat_doj.choices = antivoter_threats
    form.antivoter_threat_organizing.choices = labeled_antivoter_threats

    if form.validate_on_submit():
        state_threat_ids = form.election_state_threats.data + form.antivoter_state_threats.data
        state_threats = models.Threats.query.filter(models.Threats.id.in_(state_threat_ids))
        threat_litigation_ids = form.election_threat_litigation.data + form.antivoter_threat_litigation.data
        threat_litigation = models.Threats.query.filter(models.Threats.id.in_(threat_litigation_ids))
        threat_doj_ids = form.election_threat_doj.data + form.antivoter_threat_doj.data
        threat_doj = models.Threats.query.filter(models.Threats.id.in_(threat_doj_ids))
        threat_organizing_ids = form.election_threat_organizing.data + form.antivoter_threat_organizing.data
        threat_organizing = models.Threats.query.filter(models.Threats.id.in_(threat_organizing_ids))

        form.populate_obj(this_state)
        this_state.state_threats = state_threats.all()
        this_state.threat_litigation = threat_litigation.all()
        this_state.threat_doj = threat_doj.all()
        this_state.threat_organizing = threat_organizing.all()

        db.session.add(this_state)
        db.session.commit()
        return redirect('/edit_state')


    form.election_state_threats.data = [
        t.id for t in this_state.state_threats if int(t.threat_key) < 200
    ]
    form.election_threat_litigation.data = [
        t.id for t in this_state.threat_litigation if int(t.threat_key) < 200
    ]
    form.election_threat_doj.data = [
        t.id for t in this_state.threat_doj if int(t.threat_key) < 200
    ]
    form.election_threat_organizing.data = [
        t.id for t in this_state.threat_organizing if int(t.threat_key) < 200
    ]
    form.antivoter_threat_doj.data = [
        t.id for t in this_state.threat_doj if int(t.threat_key) > 199
    ]
    form.antivoter_state_threats.data = [
        t.id for t in this_state.state_threats if int(t.threat_key) > 199
    ]
    form.antivoter_threat_litigation.data = [
        t.id for t in this_state.threat_litigation if int(t.threat_key) > 199
    ]
    form.antivoter_threat_organizing.data = [
        t.id for t in this_state.threat_organizing if int(t.threat_key) > 199
    ]

    return render_template('edit_state.html', form=form, abbrev=abbrev)

