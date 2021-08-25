# main.py

from flask import abort, Blueprint, redirect, render_template
from flask_login import login_required, current_user

from . import models, forms, db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

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
    else:
        form = forms.OrganizationEditForm()

    if form.validate_on_submit():
        if not org:
            org = models.Groups()
        form.populate_obj(org)
        db.session.add(org)
        db.session.commit()
        return redirect('/org_find')

    return render_template('edit_org.html', form=form)
