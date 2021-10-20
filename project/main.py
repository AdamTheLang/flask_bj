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
            threat for threat in all_threats if threat.id == threat_id
        ][0]
        form = forms.ThreatForm(this_threat)
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
