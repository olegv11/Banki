from Billing.application import app, db
from Billing.models import  Bill
from flask import request, jsonify
from datetime import datetime

@app.route('/bill/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return jsonify(bill.to_dict())

@app.route('/bills', methods=['GET'])
def get_bills():
    ids = request.args.get('ids')
    bills = Bill.query.filter(Bill.id.in_(ids)).all()
    return jsonify(list(map(lambda x: x.to_dict(), bills)))


@app.route('/bill', methods=['POST'])
def create_bill():
    bill = Bill()
    bill.amount = request.values['amount']
    bill.date = datetime.utcnow()
    bill.card_number = request.values['card_number']
    bill.description = request.values['description']

    db.session.add(bill)
    db.session.commit()
    return jsonify({'id': bill.id})

@app.route('/bill/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    bill = Bill.query.get(bill_id)
    if bill is not None:
        db.session.delete(bill)
        db.session.save()
    return jsonify({})