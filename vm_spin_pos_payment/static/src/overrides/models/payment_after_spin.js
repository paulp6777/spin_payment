/** @odoo-module */

import { PaymentSpin } from "@vm_spin_pos_payment/app/payment_spin";
import { patch } from "@web/core/utils/patch";

console.log("captureAfterPayment");
patch(PaymentSpin.prototype, {
    async captureAfterPayment(line) {
        // Don't capture if the customer can tip, in that case we
        // will capture later.
        if (!this.canBeAdjusted(line.spinUID)) {
            return super.captureAfterPayment(...arguments);
        }
    },

    canBeAdjusted(spinUID) {
        var order = this.pos.get_order();
        var line = order.get_paymentline(spinUID);
       
        return (
            this.pos.config.set_tip_after_payment
        );
    },
});
