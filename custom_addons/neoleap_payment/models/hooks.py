import logging

_logger = logging.getLogger(__name__)

def post_init_hook_set_neoleap_credentials(env):
    """
    This hook is executed after the module is installed.
    It sets the NeoLeap specific credentials on the payment provider.
    """
    _logger.info("Running post_init_hook_set_neoleap_credentials...")

    neoleap_provider = env['payment.provider'].search([('code', '=', 'neoleap')], limit=1)
    if neoleap_provider:
        try:
            neoleap_provider.write({
                'neoleap_api_url': 'https://api.neoleap.com', # <--- Added this line
                'neoleap_merchant_id': '600001478',
                'neoleap_tranportal_id': 'mP45c55uHwIg0GY',
                'neoleap_tranportal_password': '$J@594K#w0sQycY',
                'neoleap_terminal_id': 'PG165100',
                'neoleap_access_token': 'BDC6AE6EEFCE2366D6E29ACF15E0F3E0',
                'neoleap_access_token_2': '28FB37B48A5CC44BEE418634721104BE0',
                'neoleap_access_token_3': 'A67467F69AC2C23C890C8E0CE9590AC2',
                'neoleap_terminal_resource_key': '51886480368351886480368351886480',
                'neoleap_terminal_resource_key_2': '51883519630151883519630151883519',
                'neoleap_terminal_resource_key_3': '51965127224751965127224751965127',
                # 'neoleap_webhook_secret': 'YOUR_WEBHOOK_SECRET_HERE', # Add your webhook secret if available
            })
            _logger.info("NeoLeap payment provider credentials set successfully.")
        except Exception as e:
            _logger.error(f"Failed to set NeoLeap payment provider credentials: {e}")
    else:
        _logger.warning("NeoLeap payment provider not found after installation.")
