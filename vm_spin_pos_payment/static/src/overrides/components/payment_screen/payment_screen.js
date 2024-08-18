/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
console.log("payment_screen JS");

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            const pendingPaymentLine = this.currentOrder.paymentlines.find(
                (paymentLine) =>
                    paymentLine.payment_method.use_payment_terminal === "spin" &&
                    !paymentLine.is_done() &&
                    paymentLine.get_payment_status() !== "pending"
            );
            if (!pendingPaymentLine) {
                return;
            }
            pendingPaymentLine.payment_method.payment_terminal.set_most_recent_spin_uid(
                pendingPaymentLine.spinUID
            );
        });
    },

    async _isOrderValid(isForceValidate) {
        console.log("_isOrderValid_isOrderValid", this.currentOrder, this.currentOrder.paymentlines[0]);
        let spinLine = this.currentOrder.paymentlines.find(
            (paymentLine) => paymentLine.payment_method.use_payment_terminal === "spin"
        );

        spinLine = this.currentOrder.paymentlines[0];
        console.log("spi_isOrderValid_isOrderValidnLine", spinLine);

        if (spinLine
            && spinLine.payment_method.split_transactions
            && spinLine.payment_method.spin_payment_default_partner
            && !this.currentOrder.get_partner()) {
            var partner = this.pos.db.get_partner_by_id(spinLine.payment_method.spin_payment_default_partner[0]);
            this.currentOrder.set_partner(partner);
        }

        return super._isOrderValid(...arguments)
    }

});
