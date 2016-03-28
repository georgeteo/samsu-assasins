from flask import Flask
from flask_wtf import Form
import wtforms
from wtforms.fields import (StringField, BooleanField, DateTimeField, IntegerField, SubmitField)

class PlayerForm(Form):
    team = StringField("Team")
    realname = StringField("Real Name")
    codename = StringField("Code Name")
    state = StringField("State")
    invul = BooleanField("Invul")
    disarm = BooleanField("Disarm")
    role = StringField("Role")
    can_set_after = DateTimeField("Can set after")
    item = IntegerField("Item")
    submit = SubmitField("Create")


class TeamForm(Form):
    to_kill = StringField("To Kill")
    target_of = StringField("Target of")
    sniper = StringField("Sniper")
    medic = StringField("Medic")
    demo = StringField("Demo")
    spy = StringField("Spy")
    submit = SubmitField("Create")
