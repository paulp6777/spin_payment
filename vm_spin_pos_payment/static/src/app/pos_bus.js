/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosBus } from "@point_of_sale/app/bus/pos_bus_service";

console.log("POS BUS JS");

patch(PosBus.prototype, {
    // Override
    dispatch(message) {
        super.dispatch(...arguments);
        console.log("BU JSSSSSSSSSSS",message)
        if (message.type === "SPIN_TERMINAL_RESPONSE" && message.payload === this.pos.config.id) {
            this.pos
                .getPendingPaymentLine("spin")
                .payment_method.payment_terminal.handleSpinStatusResponse();
        }
    },
});
