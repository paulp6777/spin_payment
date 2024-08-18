/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

console.log("JJjjjelavon_payment");

publicWidget.registry.recuring = publicWidget.Widget.extend({
    selector: '.elavon_payment',
    events: {
       
        'change #ssl_billing_cycle': '_onPaymentChange',
        'change #recurring': '_onRecurringChange',
        'change #installment_option': '_onInstallmentChange',
        'change #ssl_total_installments': '_onInstallmentNumberChange',



    },

    start: function () {
        this._super.apply(this, arguments);
        // Additional initialization code if needed
    },

    _onInstallmentChange: function (ev) {
        var self = this;
        var installment_option = $('#installment_option').val();
        console.log("666666", self, installment_option);
        jsonrpc("/elavon/installment_option", {
                installment_option:installment_option,
        }).then(function () {
            //location.reload();
        })
      
    },

    _onInstallmentNumberChange: function (ev) {
        var self = this;
        var ssl_total_installments = $('#ssl_total_installments').val();
        console.log("77777777", self, ssl_total_installments);
        jsonrpc("/elavon/ssl_total_installments", {
                ssl_total_installments:ssl_total_installments,
        }).then(function () {
            //location.reload();
        })
      
    },


    _onPaymentChange: function (ev) {
        var self = this;
        var ssl_billing_cycle = $('#ssl_billing_cycle').val();
        console.log("88888888888", self, ssl_billing_cycle);
        jsonrpc("/elavon/ssl_billing_cycle", {
                ssl_billing_cycle: ssl_billing_cycle,
        }).then(function () {
            //location.reload();
        })
      
    },

    _onRecurringChange: function (ev) {
        var self = this;
        var recurring = $('#recurring').val();
        console.log("8999999999999", self, recurring);
        jsonrpc("/elavon/recurring", {
                recurring:recurring,
        }).then(function () {
            //location.reload();
        })
      
    },


});