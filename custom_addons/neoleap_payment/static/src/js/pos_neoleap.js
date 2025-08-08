/** @odoo-module */

import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface"
import { _t } from "@web/core/l10n/translation"
import { registry } from "@web/core/registry"

export class PaymentNeoLeap extends PaymentInterface {
  setup() {
    super.setup()
    this.websocket = null
    this.currentTransaction = null
  }

  async send_payment_request(cid) {
    await super.send_payment_request(cid)

    const line = this.pos.get_order().get_paymentline(cid)
    const terminal_ip = this.payment_method.neoleap_terminal_ip || "ws://localhost:7000"

    try {
      // Connect to NeoLeap terminal via WebSocket
      await this.connectToTerminal(terminal_ip)

      // Send payment request
      const payment_data = {
        amount: line.amount,
        currency: this.pos.currency.name,
        order_ref: this.pos.get_order().name,
        terminal_ip: terminal_ip,
      }

      const result = await this.rpc("/payment/neoleap/pos_payment", payment_data)

      if (result.success) {
        line.transaction_id = result.transaction_id
        line.set_payment_status("waiting")
        return true
      } else {
        this.showPopup("ErrorPopup", {
          title: _t("Payment Error"),
          body: result.message || _t("Payment request failed"),
        })
        return false
      }
    } catch (error) {
      console.error("NeoLeap payment error:", error)
      this.showPopup("ErrorPopup", {
        title: _t("Connection Error"),
        body: _t("Could not connect to NeoLeap terminal"),
      })
      return false
    }
  }

  async connectToTerminal(terminal_ip) {
    return new Promise((resolve, reject) => {
      try {
        this.websocket = new WebSocket(terminal_ip)

        this.websocket.onopen = () => {
          console.log("Connected to NeoLeap terminal")
          resolve()
        }

        this.websocket.onerror = (error) => {
          console.error("WebSocket error:", error)
          reject(error)
        }

        this.websocket.onmessage = (event) => {
          this.handleTerminalMessage(JSON.parse(event.data))
        }

        this.websocket.onclose = () => {
          console.log("Disconnected from NeoLeap terminal")
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  handleTerminalMessage(data) {
    const line = this.pos.get_order().get_selected_paymentline()

    if (data.status === "success") {
      line.set_payment_status("done")
      line.transaction_id = data.transaction_id
    } else if (data.status === "failed") {
      line.set_payment_status("retry")
      this.showPopup("ErrorPopup", {
        title: _t("Payment Failed"),
        body: data.message || _t("Payment was declined"),
      })
    } else if (data.status === "cancelled") {
      line.set_payment_status("retry")
    }
  }

  async send_payment_cancel(order, cid) {
    await super.send_payment_cancel(order, cid)

    const line = order.get_paymentline(cid)
    if (line.transaction_id) {
      try {
        const result = await this.rpc("/payment/neoleap/pos_reverse", {
          transaction_id: line.transaction_id,
          terminal_ip: this.payment_method.neoleap_terminal_ip,
        })

        if (result.success) {
          line.set_payment_status("retry")
          return true
        }
      } catch (error) {
        console.error("NeoLeap reversal error:", error)
      }
    }

    return false
  }

  close() {
    if (this.websocket) {
      this.websocket.close()
      this.websocket = null
    }
    super.close()
  }
}

registry.category("payment_interfaces").add("neoleap", PaymentNeoLeap)
