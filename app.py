import time
import random
from flask import Flask, render_template, request, redirect, url_for,Response
from prometheus_client import Counter, generate_latest, Summary

# Creating an instance of the Flask object for the web application.
app = Flask(__name__)

# Dictionary that will store the products and their prices
products = {
    100: {'description': 'Hot Dog', 'price': 9.00},
    101: {'description': 'Double Hot Dog', 'price': 11.00},
    102: {'description': 'X-Egg', 'price': 12.00},
    103: {'description': 'X-Salad', 'price': 13.00},
    104: {'description': 'X-Bacon', 'price': 14.00},
    105: {'description': 'X-Everything', 'price': 17.00},
    200: {'description': 'Soda Can', 'price': 5.00},
    201: {'description': 'Iced Tea', 'price': 4.00}
}

view_metric = Counter('view_Product', 'Product view',['product'] )
view_duration = Summary('checkout_duration', 'Time spent in products checkout')

# Variable created to store the total purchase amount
total_value = 0
# List that stores the products of the current order.
order = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global total_value
    global order

    if request.method == 'POST':
        # Get the product code from the form
        code = int(request.form['code'])

        if code in products:
            # Add the product price to the total purchase amount
            total_value += products[code]['price']
            # Add the product description to the order
            order.append(products[code]['description'])
            message = f'{products[code]["description"]} added to the order.'
            view_metric.labels(product=products[code]['description']).inc()
        else:
            message = 'Invalid option.'

        return render_template('index.html', products=products, message=message, order=order)

    return render_template('index.html', products=products, order=order)


@app.route('/checkout', methods=['GET', 'POST'])
@view_duration.time()
def checkout():
    global total_value
    global order

    if request.method == 'POST':
        if 'submit_button' in request.form:
            if request.form['submit_button'] == 'Back':
                # Redirect to the checkout page
                return redirect(url_for('index'))
            elif request.form['submit_button'] == 'Finish':
                # Complete the order, resetting the variables
                final_value = total_value
                total_value = 0
                order = []
                return render_template('closure.html', final_value=final_value)

    return render_template('checkout.html', total_value=total_value, order=order)

@app.route('/metrics')
def metrics():
    return Response(generate_latest(),mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)

