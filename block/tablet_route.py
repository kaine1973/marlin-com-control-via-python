import os

from flask import Blueprint, render_template, request, redirect

from block.tablet import Tablet,tablets_save_path

tablet_bp = Blueprint('tablet', __name__, url_prefix='/tablet')

@tablet_bp.route('/new', methods=['GET'])
@tablet_bp.route('/edit/<int:tablet_id>', methods=['GET'])
def tablet_edit(tablet_id=None):
    if tablet_id is None:
        ids = [ int(x.split(".json")[0]) for x in os.listdir(tablets_save_path) ]
        if len(ids) == 0:
            ids = [0]
        tablet_id = max(ids) + 1
    tablet = Tablet(tablet_id)
    tablet.save_to_file()
    return render_template("tablet/edit.html", tablet=tablet)

@tablet_bp.route('/delete/<int:tablet_id>', methods=['GET'])
def tablet_delete(tablet_id):
    tablet = Tablet(tablet_id)
    tablet.delete()
    return redirect("/tablet")

@tablet_bp.route('/save', methods=['POST'])
def save_tablet():
    tablet_id = int(request.form.get("id"))
    tablet = Tablet(tablet_id)
    if tablet:
        tablet.update_settings(
            request.form.get("name"),
            int(request.form.get("nrows")),
            int(request.form.get("ncols")),
            float(request.form.get("depth_l")),
            float(request.form.get("depth_h")),
            float(request.form.get("um")),
            float(request.form.get("lm")))
    tablet.save_to_file()
    return redirect(f"/tablet/edit/{tablet_id}")


@tablet_bp.route("/", methods=['GET'])
def tablet_index():
    tablet_id = [ x.split(".json")[0] for x in os.listdir(tablets_save_path) ]
    tablets = {}
    for id in tablet_id:
        tablets[id] = Tablet(id)
    return render_template("tablet/index.html",
                           tablets=tablets)