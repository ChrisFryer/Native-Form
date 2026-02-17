from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, BooleanField, SubmitField, PasswordField, IntegerField,
)
from wtforms.validators import DataRequired, Length, Optional


class EditUserForm(FlaskForm):
    role = SelectField('Role', choices=[
        ('viewer', 'Viewer'),
        ('admin', 'Admin'),
    ], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')


class SystemSettingsForm(FlaskForm):
    registration_enabled = BooleanField('Allow self-registration')
    ldap_enabled = BooleanField('Enable LDAP authentication')
    ldap_host = StringField('LDAP Host', validators=[Optional(), Length(max=256)])
    ldap_port = IntegerField('LDAP Port', validators=[Optional()])
    ldap_use_ssl = BooleanField('Use SSL')
    ldap_base_dn = StringField('Base DN', validators=[Optional(), Length(max=256)])
    ldap_user_dn = StringField('User DN', validators=[Optional(), Length(max=256)])
    ldap_user_login_attr = StringField('Login Attribute', validators=[Optional(), Length(max=64)])
    ldap_bind_user_dn = StringField('Bind User DN', validators=[Optional(), Length(max=256)])
    ldap_bind_user_password = PasswordField('Bind Password', validators=[Optional(), Length(max=256)])
    submit = SubmitField('Save Settings')


class DefaultAWSForm(FlaskForm):
    name = StringField('Connection Name', validators=[DataRequired(), Length(max=100)])
    aws_access_key_id = StringField('Access Key ID', validators=[DataRequired()])
    aws_secret_access_key = PasswordField('Secret Access Key', validators=[DataRequired()])
    aws_default_region = SelectField('Region', choices=[
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
    ])
    submit = SubmitField('Save Default AWS')


class DefaultAzureForm(FlaskForm):
    name = StringField('Connection Name', validators=[DataRequired(), Length(max=100)])
    tenant_id = StringField('Tenant ID', validators=[DataRequired()])
    client_id = StringField('Client ID', validators=[DataRequired()])
    client_secret = PasswordField('Client Secret', validators=[DataRequired()])
    subscription_id = StringField('Subscription ID', validators=[DataRequired()])
    submit = SubmitField('Save Default Azure')
