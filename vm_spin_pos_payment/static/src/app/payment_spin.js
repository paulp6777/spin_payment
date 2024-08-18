/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { uuidv4 } from "@point_of_sale/utils";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

console.log("Spin payment js");

export class PaymentSpin extends PaymentInterface {
    /**
     * @override
     */
    setup() {
        super.setup(...arguments);
        this.paymentLineResolvers = {};
    }

    /**
     * @override
     */
    send_payment_request(cid) {
        super.send_payment_request(cid);
        return this._spin_pay(cid);
    }

    /**
     * @override
     *
     * At the moment, POS payments are no cancellable from the Mollie API.
     * It can be only cancelled from the terminal itself. If you cancel the
     * transaction from the terminal, we get notification and `handleMollieStatusResponse`
     * will handle cancellation. For force cancellation we show popup then cancel.
     */
    async send_payment_cancel(order, cid) {

        const { confirmed } = await this.env.services.popup.add(ConfirmPopup, {
            title: _t('Cancel Spin payment'),
            body: _t('First cancel transaction on POS device. Only use force cancel if that fails'),
            confirmText: _t('Force Cancel'),
            cancelText: _t('Discard')
        });

        if (confirmed) {
            super.send_payment_cancel(order, cid);
            const paymentLine = this.pending_spin_line();
            paymentLine.set_payment_status('retry');
            return true;
        }
    }

    set_most_recent_spin_uid(id) {
        this.most_recent_spin_uid = id;
    }

    pending_spin_line() {
        console.log(this.pos.getPendingPaymentLine("spin"));
        return this.pos.getPendingPaymentLine("spin");
    }

    _handle_odoo_connection_failure(data = {}) {
        var line = this.pending_spin_line();
        if (line) {
            line.set_payment_status("retry");
        }
        this._show_error(
            _t("Could not connect to the Odoo server, please check your internet connection and try again.")
        );
        return Promise.reject(data);
    }

    _submit_spin_payment(data) {
        console.log("_submit_spin_payment",data)
        return this.env.services.orm.silent
            .call('pos.payment.method', 'spin_payment_request', [
                [this.payment_method.id],
                data
            ]).catch(this._handle_odoo_connection_failure.bind(this));
    }

    _spin_pay_data() {
        var order = this.pos.get_order();
        var line = order.selected_paymentline;
        console.log("order.selected_paymentlineorder.selected_paymentline", order, order.tip_amount, this.payment_method.id);
        //console.log("uuidv4()",uuidv4(), this.most_recent_spin_uid)
        this.most_recent_spin_uid = uuidv4();
        return {
            'spin_uid': this.most_recent_spin_uid,
            'description': order.name,
            'order_id': order.uid,
            'curruncy': this.pos.currency.name,
            'amount':line.amount,
            'tip_amount':order.tip_amount,
            'session_id': this.pos.pos_session.id,
            'payment_method':this.payment_method.id,
            "trackingNumber":order.trackingNumber
        }
    }

    _spin_pay(cid) {
        var order = this.pos.get_order();
        console.log("order.selected_paymentline", order.selected_paymentline, order.is_refunded);
        /*if (order.selected_paymentline.amount < 0) {
            this._show_error(_t("Cannot process transactions with negative amount."));
            return Promise.resolve();
        }*/

        var data = this._spin_pay_data();
        var line = order.paymentlines.find((paymentLine) => paymentLine.cid === cid);
        line.setspinUID(this.most_recent_spin_uid);
        console.log("_spin_pay",data);
        return this._submit_spin_payment(data).then((data) => {
            return this._spin_handle_response(data);
        });
    }

   /* _add_tip_product(tip_amount){
        var tip_product = this.pos.db.get_product_by_id(this.pos.config.tip_product_id[0]);
        if (tip_amount >0){

            return this.add_product(tip_product, {
                    is_tip: true,
                    quantity: 1,
                    price: tip_amount,
                    lst_price: tip_amount,
                    extras: { price_type: "automatic" },
                });

        }
    }*/

    /**
     * This method handles the response that comes from Spin
     * when we first make a request to pay.
     */

    /**
    * @Override
    * @returns Promise
    */
    async _spin_handle_response(response) {
        var order = this.pos.get_order();
        var line = this.pending_spin_line();
        console.log("_spin_handle_response", line, response, response.status_code)
        // if (response.status != 'open') { comment by vml for response change
        /*if (response['Message'] != 'Approved') {
            this._show_error(response.detail);
            line.set_payment_status('retry');
            return Promise.resolve();
        }*/
        if (response['RefId']) {
            line.transaction_id = response['RefId']//response.id;
        }
        //line.set_payment_status('waitingCard');
        line.set_payment_status('Done');
        
        //return this.waitForPaymentConfirmation();
        const pollResponse = await this.pollPayment(response['RefId'], line.spinUID, order.name);
        
          

        console.log("pollResponsepollResponse 111111",pollResponse, pollResponse['status'])

        console.log("order after add tips product",order)
        //return true
        if (pollResponse['status'] != 0) {
            console.log("pollResponsepollResponse True",pollResponse)
            //let retry_remove = true
            //this._retryCountUtility(order.uid, retry_remove)
            // this._resolvePaymentStatus(true); 
            if (pollResponse['tip_amount'] >0){
                order.set_tip(pollResponse['tip_amount']);

                const line = this.pos.get_order().selected_paymentline;
                console.log("line 1111111",line);
                line.amount=line.amount +pollResponse['tip_amount']
                console.log("line 22222222",line);
                await this.captureAfterPayment(line);
            }
            return true;
             //this._resolvePaymentStatus(true)
        }
        else {
            console.log("pollResponsepollResponse False ",pollResponse, pollResponse['msg'])
            //this._incrementRetry(order.uid);
            //order._add_tip_product(pollResponse['tip_amount']);
            /*if (pollResponse['tip_amount'] >0){
                order.set_tip(pollResponse['tip_amount']);

                const line = this.pos.get_order().selected_paymentline;
                console.log("line 1111111",line);
                line.amount=line.amount +pollResponse['tip_amount']
                console.log("line 22222222",line);
                await this.captureAfterPayment(line);
            }*/
           /* if (pollResponse['tip_amount'] >0){
                    console.log("Add Tips line in order",pollResponse['tip_amount']);
                    var tip_product = this.pos.db.get_product_by_id(this.pos.config.tip_product_id[0]);
                    order.add_product(tip_product, { quantity: 1, price: pollResponse['tip_amount'], is_tip: true, });
                    return true;
                }*/
            return true;
           //this._resolvePaymentStatus(false);
        }

    }



    /**
    
     * @param { string } referenceId
     * @param { string } spinUID
     * @returns Promise
    */

    async pollPayment(referenceId, spinUID , order) {

        return this.env.services.orm.silent.call(
                    'pos.payment.method',
                    'get_spin_payment_status',
                    [[this.payment_method.id] , referenceId, spinUID, order],
                ).catch(this._handle_odoo_connection_failure.bind(this));
         }
       

    waitForPaymentConfirmation() {
        console.log("waitForPaymentConfirmation",this.pending_spin_line(),this.pending_spin_line().cid)

        var line = this.pending_spin_line().spinUID;
        console.log("lineline",line)

        // comment vml direct validate var paymentStatus = this.env.services.orm.silent
        return this.env.services.orm.silent
            .call('spin.pos.terminal.payments', 'get_spin_payment_status', [
                [],  
                line
            ]).catch(this._handle_odoo_connection_failure.bind(this));
        console.log("paymentStatuspaymentStatus", paymentStatus);
        if (!paymentStatus) {
            this._handle_odoo_connection_failure();
            return;
        }
        if (paymentStatus){

             this._resolvePaymentStatus(true); 
        }


        const resolver = this.paymentLineResolvers?.[line];
        //if (paymentStatus.status == 'paid') {
        if (paymentStatus == 'paid') {
            this._resolvePaymentStatus(true);
        } else if (['expired', 'canceled', 'failed'].includes(paymentStatus.status)) {
            this._resolvePaymentStatus(false);
        }

        //return this._handleSpinStatusResponse(line)
        /*return new Promise((resolve) => {
             console.log("resolveresolve", resolve)
             resolve=this.pending_spin_line().cid

            this.paymentLineResolvers[this.pending_spin_line().cid] = resolve;
        });*/
    }

    /**
     * This method is called from pos_bus when the payment
     * confirmation from Mollie is received via the webhook.
     */
    //async handleSpinStatusResponse() {
    _handleSpinStatusResponse(line) {

        /*var line = p_spin_line //this.pending_spin_line();
        console.log("handleSpinStatusResponse". line)
        var paymentStatus =  this.env.services.orm.silent
            .call('spin.pos.terminal.payments', 'get_spin_payment_status', [
                []], {
                //spin_uid: line.spinUID,
                //transaction_id:line.transaction_id
            })

        if (!paymentStatus) {
            this._handle_odoo_connection_failure();
            return;
        }

        var resolver = this.paymentLineResolvers?.[line.cid];
        if (paymentStatus.status == 'paid') {
           return this._resolvePaymentStatus(true);
        } else if (['expired', 'canceled', 'failed'].includes(paymentStatus.status)) {
           return  this._resolvePaymentStatus(false);
        }*/
    }

    _resolvePaymentStatus(state) {
        console.log("_resolvePaymentStatus", state)
        var line = this.pending_spin_line();
        var resolver = this.paymentLineResolvers?.[line.cid];
        if (resolver) {
            resolver(state);
        } else {
            line.handle_payment_response(state);
        }
    }

    _show_error(msg, title) {
        if (!title) {
            title = _t("Spin Error");
        }
        this.env.services.popup.add(ErrorPopup, {
            title: title,
            body: msg,
        });
    }
}
