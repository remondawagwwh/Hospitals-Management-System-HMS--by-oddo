/** @odoo-module */

import publicWidget from "@web/legacy/js/public/public_widget"

publicWidget.registry.NeoLeapPaymentForm = publicWidget.Widget.extend({
  selector: ".o_payment_form",

  start: function () {
    this._super.apply(this, arguments)

    // Handle NeoLeap payment form submission
    this.$(".o_payment_submit_button").on("click", this._onSubmitPayment.bind(this))
  },

  _onSubmitPayment: function (ev) {
    const $checkedRadio = this.$('input[name="o_payment_radio"]:checked')

    if ($checkedRadio.length && $checkedRadio.data("provider") === "neoleap") {
      ev.preventDefault()
      this._processNeoLeapPayment()
    }
  },

  _processNeoLeapPayment: function () {
    // Show loading state
    this.$(".o_payment_submit_button").prop("disabled", true).text("Processing...")

    // Submit the form - the backend will handle NeoLeap payment creation
    this.$el.submit()
  },
})

export default publicWidget.registry.NeoLeapPaymentForm
