from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, SubmitField, PasswordField, BooleanField,
)
from wtforms.validators import DataRequired, Length, Regexp, Optional


class AWSConnectionForm(FlaskForm):
    name = StringField('Connection Name', validators=[
        DataRequired(), Length(min=2, max=100),
        Regexp(r'^[a-zA-Z0-9_\-\s]+$', message='Only letters, numbers, hyphens, underscores, and spaces.')
    ])
    aws_access_key_id = StringField('Access Key ID', validators=[
        DataRequired(), Length(min=16, max=128)
    ])
    aws_secret_access_key = PasswordField('Secret Access Key', validators=[
        DataRequired(), Length(min=16, max=128)
    ])
    aws_default_region = SelectField('Default Region', choices=[
        ('us-east-1', 'US East (N. Virginia)'),
        ('us-east-2', 'US East (Ohio)'),
        ('us-west-1', 'US West (N. California)'),
        ('us-west-2', 'US West (Oregon)'),
        ('eu-west-1', 'EU (Ireland)'),
        ('eu-west-2', 'EU (London)'),
        ('eu-central-1', 'EU (Frankfurt)'),
        ('ap-southeast-1', 'Asia Pacific (Singapore)'),
        ('ap-southeast-2', 'Asia Pacific (Sydney)'),
        ('ap-northeast-1', 'Asia Pacific (Tokyo)'),
        ('ca-central-1', 'Canada (Central)'),
        ('sa-east-1', 'South America (Sao Paulo)'),
    ], validators=[DataRequired()])
    is_default = BooleanField('Set as server-wide default')
    submit = SubmitField('Save Connection')


class AzureConnectionForm(FlaskForm):
    name = StringField('Connection Name', validators=[
        DataRequired(), Length(min=2, max=100),
        Regexp(r'^[a-zA-Z0-9_\-\s]+$', message='Only letters, numbers, hyphens, underscores, and spaces.')
    ])
    tenant_id = StringField('Tenant ID', validators=[
        DataRequired(), Length(max=100)
    ])
    client_id = StringField('Client ID (App ID)', validators=[
        DataRequired(), Length(max=100)
    ])
    client_secret = PasswordField('Client Secret', validators=[
        DataRequired(), Length(max=256)
    ])
    subscription_id = StringField('Subscription ID', validators=[
        DataRequired(), Length(max=100)
    ])
    is_default = BooleanField('Set as server-wide default')
    submit = SubmitField('Save Connection')


class ConnectionFilterForm(FlaskForm):
    class Meta:
        csrf = False

    provider = SelectField('Provider', choices=[
        ('', 'All Providers'),
        ('aws', 'AWS'),
        ('azure', 'Azure'),
    ], validators=[Optional()])
