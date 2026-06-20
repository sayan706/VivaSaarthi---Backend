from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_order():
    # Mocking order creation since Razorpay is skipped
    return jsonify({'message': 'Order created (mock)', 'order_id': 'mock_order_123'}), 201

@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    # Mock webhook handler
    return jsonify({'status': 'ok'}), 200

@payments_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    return jsonify({'payment_history': []}), 200
