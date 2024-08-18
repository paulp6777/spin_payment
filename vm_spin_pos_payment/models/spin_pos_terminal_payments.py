import logging
import requests
from werkzeug import urls
import xmltodict ,json

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SpinPosTerminal(models.Model):
    _name = 'spin.pos.terminal.payments'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _description = 'Spin Pos Terminal'


    name = fields.Char("Transaction ID")
    spin_uid = fields.Char("Spin UID")
    spin_terminal_id = fields.Many2one('spin.pos.terminal', string="Spin Terminal ID")
    session_id = fields.Many2one('pos.session', string="Spin POS Session")
    spin_latest_response = fields.Json('Spin Response', default={})
    spin_latest_response_char=fields.Text("Response")
    pos_order_id=fields.Many2one('pos.order', string="POS Order")
    status = fields.Selection([
        ('paid', 'Paid'),
        ('capture', 'Capture'),
        # ('expired', 'Expired'),
        ('canceled', 'Canceled'),
        # ('pending', 'Pending'),
    ], default='open')
    amount=fields.Float('Amount')
    RefId=fields.Char('RefId')
    pos_reference=fields.Char('Pos Reference ')
    is_refund_payment=fields.Boolean('Is Refund Payment')
    transtype=fields.Selection([('Sale','Sale'),('Return','Return'),('Void', 'Void'),('Auth','Authorization'),('Pre-Auth','Pre-Auth'),('Ticket','Ticket Only'),('Capture','Capture'),('Forward','Forward'),('TipAdjust','Tips Adjust')])


    ### Capture auth payment by button 

    def capture_payment(self):

        if self.transtype =='Auth':
            capture_url=(self.spin_terminal_id.terminal_ip_address+"/cgi.html?TerminalTransaction=<request><PaymentType>Credit</PaymentType><TransType>Capture</TransType><Amount>%s</Amount><Tip>0.0</Tip><Frequency>OneTime</Frequency><InvNum></InvNum><RefId>%s</RefId><RegisterId>%s</RegisterId><AuthKey>%s</AuthKey><PrintReceipt>%s</PrintReceipt><SigCapture>%s</SigCapture></request>" % (float(self.amount),self.name,self.spin_terminal_id.register_id, self.spin_terminal_id.auth_key, self.spin_terminal_id.printreceipt, self.spin_terminal_id.sigcapture))

            print("capture_url", capture_url)
            result=requests.get(capture_url)

            print("Result", result, result.content)
            xml_json = xmltodict.parse(result.content)
            res_json=json.dumps(xml_json)
            resp = json.loads(res_json)
            print("resp['xmp']['response']",resp['xmp']['response'],  resp['xmp']['response']['Message'])  
            response=resp['xmp']['response']  
            if resp['xmp']['response']['Message'] == 'Approved':
                self.status='capture'
            else:
                raise ValidationError(_("Payment status cancelled by terminal"))


    def _create_spin_payment_request(self, response, data):
        print("_create_spin_payment_request555",data.get('description'), response, data, response['Message'])
        if response :#and response.get('status') == 'open':
        
            var=self.create({
                'name': response.get('RefId'),#response.get('id'),
                'spin_uid': data.get('spin_uid'),
                'spin_terminal_id': data.get('spin_terminal_id'),
                'session_id': data.get('session_id'),
                'spin_latest_response': response,
                'spin_latest_response_char':response,
                'status':"paid" if response['Message'] == 'Approved' else 'canceled',                
                'amount':data.get('amount'),
                'RefId':response['RefId'],
                'transtype':data.get('transtype'),
                'pos_reference':data.get('description'),
                'is_refund_payment':data.get('is_refund_payment')

            })
            print("Create terminal payment record ",var)
            return True



    @api.model
    def spin_cancel_payment_request(self, transaction_id=None, spin_uid=None):
        domain = []
        if transaction_id:
            domain.append(('name', '=', transaction_id))
        elif spin_uid:
            domain.append(('spin_uid', '=', spin_uid))
        else:
            return {}
        spin_payment = self.search(domain, limit=1)
        if spin_payment and spin_payment.status == 'open':
            return spin_payment.terminal_id._api_cancel_spin_payment(spin_payment.name)
        return {}

    def _spin_process_webhook(self, webhook_data):
        print("webhook_datawebhook_data00",webhook_data)
        spin_payment = self.sudo().search([('name', '=', webhook_data.get('id'))], limit=1)
        if spin_payment:
            payment_status = spin_payment.terminal_id._api_get_spin_payment_status(webhook_data.get('id'))
            if payment_status and payment_status.get('status'):
                spin_payment.write({
                    'spin_latest_response': payment_status,
                    'status': payment_status.get('status')
                })
                self.env["bus.bus"].sudo()._sendone(spin_payment.session_id._get_bus_channel_name(), "SPIN_TERMINAL_RESPONSE", spin_payment.session_id.config_id.id)