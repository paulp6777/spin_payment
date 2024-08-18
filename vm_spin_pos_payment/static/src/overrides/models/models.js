/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { Payment } from "@point_of_sale/app/store/models";
import { PaymentSpin } from "@vm_spin_pos_payment/app/payment_spin";
import { patch } from "@web/core/utils/patch";

register_payment_method("spin", PaymentSpin);

console.log('Spin Payment model JS');

patch(Payment.prototype, {
    setup() {
        super.setup(...arguments);
        this.spinUID = this.spinUID || null;
    },
    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        //console.log("export_as_JSON",json);
        if (json) {
            json.spin_uid = this.spinUID;
        }
        return json;
    },
    //@override
    init_from_JSON(json) {
        //console.log("init_from_JSON",json);
        super.init_from_JSON(...arguments);
        this.spinUID = json.spin_uid;
    },
    setspinUID(id) {
        this.spinUID = id;
    },
});
