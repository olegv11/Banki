from Billing.application import app, db
from Billing.models import  Bill
from flask import request, jsonify
from datetime import datetime

@app.route('/bill/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return jsonify(bill)

@app.route('/bill', methods=['POST'])
def create_bill():
    bill = Bill()
    bill.amount = request.values['amount']
    bill.date = datetime.utcnow()
    bill.card_number = request.values['card_number']
    bill.description = request.values['description']

    db.session.add(bill)
    db.session.commit()
