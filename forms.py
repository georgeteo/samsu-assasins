from flask import Flask
from flask_wtf import Form
from wtforms.fields import (StringField, BooleanField, DateTimeField, IntegerField, SubmitField)
from wtforms.widgets import CheckboxInput

class PlayerForm(Form):
    team = StringField(label="Team")
    realname = StringField("Real Name")
    codename = StringField("Code Name")
    state = StringField("State")
    invul = StringField("Invul")
    disarm = StringField("Disarm")
    role = StringField("Role")
    can_set_after = StringField("Can set after")
    item = StringField("Item")
    submit = SubmitField("Submit")


class TeamForm(Form):
    to_kill = StringField("To Kill")
    target_of = StringField("Target of")
    sniper = StringField("Sniper")
    medic = StringField("Medic")
    demo = StringField("Demo")
    spy = StringField("Spy")
    submit = SubmitField("Submit")

class BombForm(Form):
    attacker = StringField("Attacker")
    place = StringField("Place")
    time = StringField("Time")
    trigger = StringField("Trigger")
    deprecated = StringField("Deprecated")

class InvulForm(Form):
   medic = StringField("Medic")
   target = StringField("Target")
   start_time = StringField("Start Time")
   end_time = StringField("End Time")
   in_effect = StringField("In Effect")
   deprecated = StringField("Deprecated")

class DisarmForm(Form):
    attacker = StringField("Attacker")
    victim = StringField("Victim")
    startime = StringField("Start Time")
    endtime = StringField("End Time")
    deprecated = StringField("Deprecated")
    
