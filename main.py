from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
shop_id = '5'
secretKey = 'SecretKey01'
payway = 'advcash_rub'
currency_code = {'EUR': '978', 'USD': '840', 'RUB': '643'}


def sign_gen(**params):
    sorted_keys = sorted(params.keys())
    sign = ''
    for key in sorted_keys:
        sign += str(params[key])
        if key != 'shop_order_id':
            sign += ':'
    sign += secretKey
    print(sign)
    return sha256(sign.encode('utf-8')).hexdigest()


class Receipt:
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(5), nullable=False)
    dispatch_time = db.Column(db.Time, nullable=False)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/pay', methods=['POST', 'GET'])
def pay():
    if request.method == 'POST':
        amount = request.form['amount']
        currency = request.form['currency']
        description = request.form['description']
        if currency == '978':
            sign = sign_gen(amount=amount, currency=currency, shop_id=shop_id, shop_order_id=2)
            res = requests.post('https://pay.piastrix.com/ru/pay', params={'amount': amount, 'currency': currency,
                                                                           'shop_id': shop_id, 'shop_order_id': 2,
                                                                           'sign': sign})
            print(res.text)
            return render_template('index.html')
            # return render_template('pay.html', amount=amount, currency=currency, sign=sign, shop_id=shop_id, shop_order_id=2)
        elif currency == '840':
            sign = sign_gen(payer_currency=currency, shop_amount=amount, shop_currency=currency, shop_id=shop_id,
                            shop_order_id=2)
            response = requests.post('https://core.piastrix.com/bill/create', json={'shop_amount': amount,
                                                                               'shop_currency': currency,
                                                                               'shop_id': shop_id, 'shop_order_id': 2,
                                                                               'payer_currency': currency,
                                                                               'description': description,
                                                                               'sign': sign})
            response_url = (response.json()['data']['url'])

            return redirect(response_url)
    else:
        return render_template('pay.html')


if __name__ == "__main__":
    app.run(debug=True)

