import logging
import json
from datetime import datetime
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    neoleap_transaction_id = fields.Char(
        string='NeoLeap Transaction ID',
        help='Transaction ID from NeoLeap'
    )
    neoleap_payment_url = fields.Char(
        string='NeoLeap Payment URL',
        help='URL for redirecting customer to NeoLeap payment page'
    )

    def _get_specific_rendering_values(self, processing_values):
        """ Override to add NeoLeap-specific rendering values. """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'neoleap':
            return res

        # Prepare payment data for NeoLeap
        payment_data = self._neoleap_prepare_payment_data()
        
        # Create payment request
        try:
            response = self.provider_id._neoleap_make_request('payment/create', payment_data)
            
            if response.get('success'):
                self.neoleap_transaction_id = response.get('transaction_id')
                self.neoleap_payment_url = response.get('payment_url')
                
                res.update({
                    'api_url': self.neoleap_payment_url,
                    'neoleap_data': payment_data,
                })
            else:
                raise UserError(_('Failed to create payment request: %s') % response.get('message', 'Unknown error'))
                
        except Exception as e:
            _logger.error(f'NeoLeap payment creation failed: {e}')
            raise UserError(_('Payment initialization failed. Please try again.'))

        return res

    def _neoleap_prepare_payment_data(self):
        """ Prepare payment data for NeoLeap API """
        base_url = self.provider_id.get_base_url()
        
        return {
            'merchant_id': self.provider_id.neoleap_merchant_id,
            'amount': str(self.amount),
            'currency': self.currency_id.name,
            'order_id': self.reference,
            'description': f'Payment for Order {self.reference}',
            'customer_email': self.partner_email or '',
            'customer_name': self.partner_name or '',
            'return_url': urls.url_join(base_url, '/payment/neoleap/return'),
            'cancel_url': urls.url_join(base_url, '/payment/neoleap/cancel'),
            'webhook_url': urls.url_join(base_url, '/payment/neoleap/webhook'),
            'metadata': {
                'odoo_transaction_id': self.id,
                'partner_id': self.partner_id.id if self.partner_id else None,
            }
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override to handle NeoLeap notification data. """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'neoleap' or len(tx) == 1:
            return tx

        # Look for transaction by NeoLeap transaction ID
        neoleap_tx_id = notification_data.get('transaction_id')
        if neoleap_tx_id:
            tx = self.search([('neoleap_transaction_id', '=', neoleap_tx_id)])

        # Look for transaction by reference
        if not tx:
            reference = notification_data.get('order_id')
            if reference:
                tx = self.search([('reference', '=', reference)])

        return tx

    def _process_notification_data(self, notification_data):
        """ Override to process NeoLeap notification data. """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'neoleap':
            return

        # Update transaction with NeoLeap data
        self.neoleap_transaction_id = notification_data.get('transaction_id')
        
        # Determine transaction state based on NeoLeap status
        status = notification_data.get('status', '').lower()
        if status == 'success':
            self._set_done()
        elif status == 'failed':
            self._set_error("Payment failed")
        elif status == 'cancelled':
            self._set_canceled()
        else:
            self._set_pending()

    @api.model
    def _neoleap_form_get_tx_from_data(self, data):
        """ Extract transaction from NeoLeap return data. """
        reference = data.get('order_id')
        if not reference:
            raise ValidationError(_('NeoLeap: missing order_id in return data'))

        tx = self.search([('reference', '=', reference)])
        if not tx:
            raise ValidationError(_('NeoLeap: no transaction found for reference %s') % reference)

        return tx

    def _neoleap_form_validate(self, data):
        """ Validate NeoLeap return data and update transaction. """
        status = data.get('status', '').lower()
        
        if status == 'success':
            self._set_done()
            return True
        elif status == 'failed':
            self._set_error(data.get('message', 'Payment failed'))
            return False
        elif status == 'cancelled':
            self._set_canceled()
            return False
        else:
            self._set_pending()
            return False
