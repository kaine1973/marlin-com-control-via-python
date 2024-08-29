import json
import os.path

from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.exceptions import BadRequest
from basic import row_count, col_count
from .block import Block, Layout, layouts_save_path
from .tablet import tablets_save_path, Tablet

block_bp = Blueprint('block', __name__, url_prefix='/block')


@block_bp.route("/<int:block_id>/edit", methods=['GET'])
def block_edit(block_id):
    block = Block(block_id)
    return render_template("block/edit_block.html", block=block)

@block_bp.route("/query/<int:block_id>", methods=['GET'])
def block_query(block_id):
    block = Block(block_id)
    return block.to_json()

@block_bp.route("/save", methods=['POST'])
def block_save():
    block_id = request.form.get("block_id")
    if block_id:
        block = Block(block_id)
        block.position_rb = [float(request.form.get("position_rb_x")), float(request.form.get("position_rb_y"))]
        block.position_lt = [float(request.form.get("position_lt_x")), float(request.form.get("position_lt_y"))]
        block.block_name = request.form.get("name")
        block.save_to_file()
        return redirect(f"/block/{block_id}/edit")
    else:
        raise BadRequest("Block ID must be provided")

@block_bp.route('/layout_save', methods=['POST'])
def layout_save():
    layout_id = request.form.get('id')
    layout_name = request.form.get('name')
    layout_config = request.form.get('config')
    layout = Layout(layout_id)
    layout.name = layout_name
    for k,v in json.loads(layout_config).items():
        layout.add_config(k,v)
    layout.save_to_file()
    return {'code': 200,
            'message': "保存成功"}

@block_bp.route('/layout_add', methods=['GET'])
@block_bp.route('/layout_edit/<int:layout_id>', methods=['GET'])
def layout_edit(layout_id = None):
    if layout_id is None:
        ids = [int(x.split(".json")[0]) for x in os.listdir(layouts_save_path)]
        if len(ids) == 0:
            ids = [0]
        layout_id = max(ids) + 1
    layout = Layout(layout_id)
    #get all blocks
    blocks = {}
    for row in range(row_count):
        for col in range(col_count):
            number = (col * col_count) + (row + 1)
            blocks[number] = Block(number)
    # get_all_tables
    tablet_id = [x.split(".json")[0] for x in os.listdir(tablets_save_path)]
    tablets = {}
    for id in tablet_id:
        tablets[id] = Tablet(id)
    return render_template('block/layout_edit.html',
                           row_count=row_count,
                           col_count=col_count,
                           layout=layout,
                           blocks=blocks,
                           tablets=tablets)

@block_bp.route("/tablet_layout", methods=['GET'])
def tablet_layout():
    layout_ids = [ x.split(".json")[0] for x in os.listdir(layouts_save_path) ]
    layouts = {}
    for layout_id in layout_ids:
        layouts[layout_id] = Layout(layout_id)
    return render_template('block/layout_list.html', layouts=layouts)

@block_bp.route("/", methods=['GET'])
def block_index():
    blocks = {}
    for row in range(row_count):
        for col in range(col_count):
            number = (col * col_count) + (row + 1)
            blocks[number] = Block(number)
    return render_template("block/index.html",
                           row_count=row_count,
                           col_count=col_count,
                           blocks=blocks)
