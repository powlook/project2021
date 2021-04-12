# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from app.home.models import Order, OrderProduct, ForecastArima, ForecastSarima, ForecastLSTM, ForecastRollingMA
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import sqlalchemy as sa

@blueprint.route('/index')
@login_required
def index():

    return render_template('dashboard.html', segment='index')

### Views
@blueprint.route('/orders', methods=['GET'])
@login_required
def orders():
    orders = Order.query.limit(5).all()
    return render_template( 'orders.html', orders=orders, segment='orders', title="Orders")

@blueprint.route('/products', methods=['GET'])
@login_required
def products():
    orders = Order.query.limit(5).all()
    return render_template( 'products.html', orders=orders, segment='products', title="Products")

@blueprint.route('/inventory', methods=['GET'])
@login_required
def inventory():
    orders = Order.query.limit(5).all()
    return render_template( 'inventory.html', orders=orders, segment='inventory', title="Inventory")

@blueprint.route('/order-forecasting', methods=['GET'])
@login_required
def order_forecasting():
    forecastArima = ForecastArima.serialize_list(ForecastArima.query.all())
    forecastSarima = ForecastSarima.serialize_list(ForecastSarima.query.all())
    forecastLSTM = ForecastLSTM.serialize_list(ForecastLSTM.query.all())
    forecastRollingMA = ForecastRollingMA.serialize_list(ForecastRollingMA.query.all())
    forecasts = {
        'recommended': forecastLSTM,
        'arima': forecastArima,
        'sarima': forecastSarima,
        'lstm': forecastLSTM,
        'rolling-ma': forecastRollingMA
    }
    orderproducts = OrderProduct.group_by_product()

    formatted_op = []
    for op in orderproducts:
        p = {
            'date': op.date,
            'sku': op.product_sku,
            'qty': int(op.quantity),
        }
        formatted_op.append(p)

    return render_template('order-forecasting.html', orderproducts=formatted_op, forecasts=forecasts, segment='order-forecasting', title="Order Forecasting")

### API
@blueprint.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    orders = Order.query.limit(5).all()
    return jsonify(Order.serialize_list(orders))
    # return jsonify({ 'order_id': 1, 'name': 'ABC' }, { 'order_id': 2, 'name': 'CDEF' })

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  
