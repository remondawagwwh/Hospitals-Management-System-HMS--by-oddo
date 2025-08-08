import logging
import requests
import json
import hashlib
import hmac
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('neoleap', 'NeoLeap')],
        ondelete={'neoleap': 'set default'}
    )
    
    # NeoLeap specific fields
    neoleap_merchant_id = fields.Char(
        string='Merchant ID',
        help='Your NeoLeap Merchant ID',
        required_if_provider='neoleap'
    )
    neoleap_tranportal_id = fields.Char(
        string='Tranportal ID',
        help='Your NeoLeap Tranportal ID',
        required_if_provider='neoleap'
    )
    neoleap_tranportal_password = fields.Char(
        string='Tranportal Password',
        help='Your NeoLeap Tranportal Password',
        required_if_provider='neoleap'
    )
    neoleap_terminal_id = fields.Char(
        string='Terminal ID',
        help='Your NeoLeap Terminal ID',
        required_if_provider='neoleap'
    )
    neoleap_access_token = fields.Char(
        string='Terminal Resource Key ID',
        help='Your NeoLeap Terminal Resource Key ID (Primary)',
        required_if_provider='neoleap'
    )
    neoleap_access_token_2 = fields.Char(
        string='Terminal Resource Key ID 2',
        help='Your NeoLeap Terminal Resource Key ID (Secondary)'
    )
    neoleap_access_token_3 = fields.Char(
        string='Terminal Resource Key ID 3',
        help='Your NeoLeap Terminal Resource Key ID (Tertiary)'
    )
    neoleap_terminal_resource_key = fields.Char(
        string='Terminal Resource Key',
        help='Your NeoLeap Terminal Resource Key (Primary)'
    )
    neoleap_terminal_resource_key_2 = fields.Char(
        string='Terminal Resource Key 2',
        help='Your NeoLeap Terminal Resource Key (Secondary)'
    )
    neoleap_terminal_resource_key_3 = fields.Char(
        string='Terminal Resource Key 3',
        help='Your NeoLeap Terminal Resource Key (Tertiary)'
    )
    neoleap_api_url = fields.Char(
        string='API URL',
        default='https://api.neoleap.com',
        help='NeoLeap API Base URL',
        required_if_provider='neoleap'
    )
    neoleap_webhook_secret = fields.Char(
        string='Webhook Secret',
        help='Secret key for webhook signature verification'
    )

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override to filter NeoLeap provider based on currency. """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)
        currency = self.env['res.currency'].browse(currency_id) if currency_id else None
        
        if currency and currency.name not in ['SAR', 'USD', 'EUR']:
            providers = providers.filtered(lambda p: p.code != 'neoleap')
            
        return providers

    def _neoleap_make_request(self, endpoint, data=None, method='POST'):
        """ Make API request to NeoLeap """
        if not self.neoleap_api_url or not self.neoleap_access_token:
            raise UserError(_('NeoLeap API configuration is incomplete'))
            
        url = f"{self.neoleap_api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f'Bearer {self.neoleap_access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error(f'NeoLeap API request failed: {e}')
            raise UserError(_('Payment processing failed. Please try again.'))

    def _get_default_payment_method_codes(self):
        """ Override to add NeoLeap payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code == 'neoleap':
            return ['card']
        return default_codes
