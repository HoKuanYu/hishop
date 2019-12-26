from flask import redirect, render_template, url_for, flash, request, abort
from flask.views import MethodView
from flask_login import current_user

from app.models.user import User
from app.models.message import Message

from mongoengine.queryset.visitor import Q

class HiChatUpdate(MethodView):
    def get(self):
        pass

    def post(self):
        senderID = request.values["senderID"]
        receiverID = request.values["receiverID"]        
        if senderID != str(current_user.id):
            abort(403)
        
        messages = Message.objects((Q(sender_id=senderID) & Q(receiver_id=receiverID)) | (Q(sender_id=receiverID) & Q(receiver_id=senderID))).order_by("+create_time")
        return messages.to_json()