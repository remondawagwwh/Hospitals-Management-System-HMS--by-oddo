from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    use_payment_terminal = fields.Selection(
        selection_add=[('neoleap', 'NeoLeap Terminal')],
        ondelete={'neoleap': 'set default'}
    )
    
    neoleap_terminal_ip = fields.Char(
        string='NeoLeap Terminal IP',
        help='IP address and port for NeoLeap terminal (e.g., ws://localhost:7000)',
        default='ws://localhost:7000'
    )

    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal_neoleap(self):
        if self.use_payment_terminal == 'neoleap':
            self.name = 'Card'
