from Statistics.application import app, db
from Statistics.models import StatisticsItem
from flask import request, jsonify
import werkzeug.exceptions

def average(type):
    data = StatisticsItem.query.filter_by(type=type).all()
    if not data:
        return 0.0
    return sum(map(float, data)) / len(data)


def all(type):
    return StatisticsItem.query.filter_by(type=type).all()


operations = {
    'AVG': average,
    'ALL': all
}


@app.route('/data', methods=['POST'])
def save_datum():
    item = StatisticsItem()
    item.type = request.values['type']
    item.data = request.values.get('data', default='')

    db.session.add(item)
    db.session.commit()
    return jsonify({})


@app.route('/data', methods=['GET'])
def get_datum():
    type = request.args.get('type')
    operation = request.args.get('operation', default='ALL')

    if type not in operations:
        raise werkzeug.exceptions.BadRequest('Operation not supported')

    result = operation['type']()
    return jsonify({'result': result})
