from flask import redirect, render_template, url_for, request, flash, abort
from flask.views import MethodView
from flask_login import current_user, login_required
from wtforms import SubmitField, TextAreaField, HiddenField, StringField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo, ValidationError

from app.models.order import Order, ORDER_STATUS
from app.models.product import Product, PRODUCT_STATUS
from app.models.user import User

from app import app
from app.socketioService import sendMessageViaSocketIO

import datetime

#移交中 領收中 已完成 已取消 全部
#ORDER_STATUS = {"TRANSFERING" : "0", "RECEIPTING" : "1", "COMPLETE" : "2", "CANCEL" : "3", "ALL" : "4"}
class PurchaseListView(MethodView):
    def get(self):
        form = PerchaseListForm()
        status = request.args.get('status')

        if status == ORDER_STATUS['TRANSFERING']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["TRANSFERING"])
        elif status == ORDER_STATUS['RECEIPTING']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["RECEIPTING"])
        elif status == ORDER_STATUS['COMPLETE']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["COMPLETE"])
        elif status == ORDER_STATUS['CANCEL']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["CANCEL"])
        else:
            status = ORDER_STATUS["ALL"]
            orders = Order.objects(buyer_id=current_user.id)
        print(orders)
        orders = sorted(orders, key=lambda k: k.create_time, reverse=False)


        return render_template('user/product/list.html', orders=orders, ORDER_STATUS=ORDER_STATUS, status=status, form=form)
    def post(self):
        form = PerchaseListForm()
        status = request.args.get('status')
        if status == ORDER_STATUS['TRANSFERING']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["TRANSFERING"])
        elif status == ORDER_STATUS['RECEIPTING']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["RECEIPTING"])
        elif status == ORDER_STATUS['COMPLETE']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["COMPLETE"])
        elif status == ORDER_STATUS['CANCEL']:
            orders = Order.objects(buyer_id=current_user.id, status=ORDER_STATUS["CANCEL"])
        else:
            status = ORDER_STATUS["ALL"]
            orders = Order.objects(buyer_id=current_user.id)
        #print(orders)
        orders = sorted(orders, key=lambda k: k.create_time, reverse=False)

        if 'score' not in request.form:
            flash('請點選評價星星',category='error')

        if form.validate_on_submit() and 'score' in request.form:   
            order = Order.objects(product_id=request.values['commentProductID'],buyer_id=current_user.id).first()
            if order == None:
                abort(404)
            else:
                if str(order.status) != ORDER_STATUS['RECEIPTING']:
                    abort(404)
                else:
                    #order implementaion
                    order.buyer_comment = form.detail.data      
                    order.buyer_rating = request.values['score']  
                    order.status = int(ORDER_STATUS['COMPLETE'])
                    order.finish_time = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
                    order.save()
                    #seller implementation
                    seller = User.objects(id=order.product_id.seller_id.id).first()
                    if order.product_id.bidding:
                        seller.hicoin += order.product_id.bid.now_price*0.88
                    else:
                        seller.hicoin += order.product_id.price*0.88
                    seller.save()
                    
                    print(request.values['score'])   
        
                    #return render_template('user/product/list.html', orders=orders, ORDER_STATUS=ORDER_STATUS, status=status, form=form)
        return redirect(url_for('user.purchase_list',status='4'))
        
#update the browser cache, let the image be correct on window 
@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

# for comment
class PerchaseListForm(FlaskForm):
    detail = StringField("評論")
    submit = SubmitField('提交')
    
    