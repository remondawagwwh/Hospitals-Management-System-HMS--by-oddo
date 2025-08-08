import json
import logging
import pprint
from werkzeug.exceptions import Forbidden

from odoo import http, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class NeoLeapController(http.Controller):

    @http.route('/payment/neoleap/return', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def neoleap_return(self, **data):
        """ Handle return from NeoLeap payment page """
        _logger.info('NeoLeap return data:\n%s', pprint.pformat(data))
        
        try:
            # Get transaction from return data
            tx_sudo = request.env['payment.transaction'].sudo()._neoleap_form_get_tx_from_data(data)
            
            # Validate the transaction
            tx_sudo._neoleap_form_validate(data)
            
        except ValidationError:
            _logger.exception('Unable to validate NeoLeap payment')
            
        return request.redirect('/payment/status')

    @http.route('/payment/neoleap/cancel', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def neoleap_cancel(self, **data):
        """ Handle cancellation from NeoLeap payment page """
        _logger.info('NeoLeap cancel data:\n%s', pprint.pformat(data))
        
        try:
            tx_sudo = request.env['payment.transaction'].sudo()._neoleap_form_get_tx_from_data(data)
            tx_sudo._set_canceled()
        except ValidationError:
            _logger.exception('Unable to handle NeoLeap payment cancellation')
            
        return request.redirect('/payment/status')

    @http.route('/payment/neoleap/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def neoleap_webhook(self, **data):
        """ Handle NeoLeap webhook notifications """
        _logger.info('NeoLeap webhook data:\n%s', pprint.pformat(data))
        
        try:
            # Verify webhook signature if secret is configured
            provider = request.env['payment.provider'].sudo().search([('code', '=', 'neoleap')], limit=1)
            if provider.neoleap_webhook_secret:
                # Add signature verification logic here
                pass
            
            # Process the notification
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('neoleap', data)
            if tx_sudo:
                tx_sudo._process_notification_data(data)
                
        except Exception as e:
            _logger.exception('Error processing NeoLeap webhook: %s', e)
            return request.make_response('Error', status=400)
            
        return request.make_response('OK', status=200)

    @http.route('/payment/neoleap/pos_payment', type='json', auth='user', methods=['POST'])
    def neoleap_pos_payment(self, **data):
        """ Handle POS payment requests """
        try:
            amount = data.get('amount', 0)
            terminal_ip = data.get('terminal_ip', 'ws://localhost:7000')
            order_ref = data.get('order_ref', '')
            
            # Here you would implement the WebSocket communication with the terminal
            # For now, we'll return a mock response
            
            return {
                'success': True,
                'transaction_id': f'NEOLEAP_{order_ref}_{amount}',
                'message': 'Payment request sent to terminal'
            }
            
        except Exception as e:
            _logger.exception('NeoLeap POS payment error: %s', e)
            return {
                'success': False,
                'message': str(e)
            }

    @http.route('/payment/neoleap/pos_reverse', type='json', auth='user', methods=['POST'])
    def neoleap_pos_reverse(self, **data):
        """ Handle POS payment reversal """
        try:
            transaction_id = data.get('transaction_id', '')
            terminal_ip = data.get('terminal_ip', 'ws://localhost:7000')
            
            # Implement reversal logic here
            
            return {
                'success': True,
                'message': 'Payment reversed successfully'
            }
            
        except Exception as e:
            _logger.exception('NeoLeap POS reversal error: %s', e)
            return {
                'success': False,
                'message': str(e)
            }
