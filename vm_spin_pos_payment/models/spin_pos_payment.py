import logging
import requests
from werkzeug import urls
import xmltodict, json

from odoo import fields, models,api , _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

Status_url='https://spinpos.net/spin/GetTerminalStatus?RegisterID='

class SpimPosTerminal(models.Model):
    _name = 'spin.pos.terminal'
    _description = 'Spin Pos Terminal'

    name = fields.Char()
    terminal_ip_address = fields.Char('Terminal IP Address')
    cgi_port = fields.Char(' CGI Port')
    auth_key = fields.Char('Auth key')
    register_id = fields.Char(' Register ID')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ])
    currency_id = fields.Many2one('res.currency', string='Currency')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    printreceipt=fields.Selection([('both','Both'),('customer','Customer'),('merchant','Merchant'),('no','No')], default="both")
    sigcapture=fields.Selection([('yes','Yes'),('no','No')], default='no')
    void_time=fields.Float()
    transtypes=fields.Selection([('Sale','Sale'),('Return','Return'),('Void', 'Void'),('Auth','Authorization'),('Ticket','Ticket Only'),('Capture','Capture'),('Forward','Forward'),('TipAdjust','Tips Adjust')],default='Sale')
    partner_code=fields.Char("Partner Code", required="1")

    @api.constrains('partner_code')
    def _check_partner_code(self):

        if self.partner_code != '678odoo#%@123':
             raise ValidationError(_("To activate you need an Elavon MerchantID , please contact us at 1-800-403-3297 or Support@intruxtmerchantservices.com"))


    def terminal_status(self):
        if self.register_id:
            if self.terminal_ip_address:                
                url=self.terminal_ip_address+str('/GetTerminalStatus?RegisterID=')+str(self.register_id)
                response = requests.get(url)#requests.request(method, url, json=data, headers=headers, timeout=60)
                print("terminal status ",response, response.text)
                if response.text =='Online':
                    print("terminal status  status_code",response.status_code)
                    self.status='active'
                    return True
                else:
                    raise ValidationError(_("Payment Terminal is Offline mode."))
                    return False

            return  response

    def _prepare_payment_payload(self, data):
        base_url = self.get_base_url()
        webhook_url = urls.url_join(base_url, '/pos_mollie/webhook/')
        print("_prepare_payment_payload_prepare_payment_payload",data)
        xml =   """<?xml version='1.0' encoding='utf-8'?>
                    <request>
                        <PaymentType>debit</PaymentType><TransType>Sale</TransType>
                        <Amount>1.00</Amount>
                        <InvNum>1</InvNum>
                        <RefId>256</RefId>
                        <AuthKey>H2axj8U4QT3</AuthKey>
                        <RegisterId>9028094</RegisterId>
                        <PrintReceipt>Both</PrintReceipt>
                    </request>
                """
            
        return {
            "amount": f"{data['amount']:.2f}",
            "description": data['description'],
            #"webhookUrl": webhook_url,
           # "redirectUrl": webhook_url,
            "method": "pointofsale",
            "terminalId": self.terminal_ip_address,
            "metadata": {
               # "spin_uid": data['spin_uid'],
                "order_id": data['order_id'],
            }
        }


    def _api_make_payment_request(self, data):
        print("_api_make_payment_request_api_make_payment_request",data)
        #count=7
        transtype=""
        amount=float(data.get('amount'))
        if data.get('payment_method'):
            print("data.get('payment_method')",data.get('payment_method'))
            payment_method_id=self.env['pos.payment.method'].search([('id','=',data.get('payment_method'))], limit=1)
          

            if payment_method_id:
                if payment_method_id.spin_pos_terminal_id.transtypes == 'Auth' and data.get('amount') > 0:
                    print("payment_method_idpayment_method_idpayment_method_id",payment_method_id)
                    transtype="Auth"


                elif data.get('amount') < 0:
                    transtype="Return"
                    amount=-(amount)
                else:
                    transtype="Sale"       
        print("transtypetranstype",transtype)
        
        order= str(data.get('order_id'))#+str(count)
        if self.terminal_ip_address:
            final_url=(self.terminal_ip_address+"/cgi.html?TerminalTransaction=<request><PaymentType>Credit</PaymentType><TransType>%s</TransType><Amount>%s</Amount><Tip>0.0</Tip><Frequency>OneTime</Frequency><InvNum></InvNum><RefId>%s</RefId><RegisterId>%s</RegisterId><AuthKey>%s</AuthKey><PrintReceipt>%s</PrintReceipt><SigCapture>%s</SigCapture></request>" % (transtype,float(amount),order,self.register_id, self.auth_key, self.printreceipt, self.sigcapture))

            print("final_url", final_url)
            
            #result=requests.get('https://spinpos.net:443/spin/cgi.html?TerminalTransaction=<request><PaymentType>Debit</PaymentType><TransType>Sale</TransType><Amount>8.50</Amount><Tip>0.00</Tip><Frequency>OneTime</Frequency><InvNum></InvNum><RefId>656666</RefId><RegisterId>51846016</RegisterId><AuthKey>XfpSMT3Huu</AuthKey><PrintReceipt>Both</PrintReceipt><SigCapture>No</SigCapture></request>')
            result=requests.get(final_url)
            print("Result", result, result.content, type(result.content))
            xml_json = xmltodict.parse(result.content)
            res_json=json.dumps(xml_json)
            resp = json.loads(res_json)
            
            if resp['xmp']['response']['ResultCode'] == 1:
                self.env['spin.pos.terminal.payments']._create_spin_payment_request(resp['xmp']['response'], {**data, 'spin_terminal_id':self.id, 'transtype':transtype})
                return  resp['xmp']['response']
            else:
                self.env['spin.pos.terminal.payments']._create_spin_payment_request(resp['xmp']['response'], {**data, 'spin_terminal_id':self.id, 'transtype':transtype})
                return resp['xmp']['response']

      
        else:
            raise ValidationError(_("Payment Terminal is Offline mode++."))

    def _api_get_spin_payment_status(self, transaction_id):
        print("_api_get_spin_payment_status_api_get_spin_payment_status",transaction_id)
        return  True#self.sudo()._mollie_api_call(f'/payments/{transaction_id}', method='GET', silent=True)


    # =====================
    # GENERIC TOOLS METHODS
    # =====================

    def _spin_api_call(self, endpoint, data=None, method='POST', silent=False):
        company = self.company_id or self.env.company

        headers = {
            'content-type': 'application/xml',
           # "Authorization": f'Bearer {company.mollie_terminal_api_key}',
        }

        #endpoint = f'/v2/{endpoint.strip("/")}'
        url = 'http://spinpos.net/spin' #urls.url_join('https://spinpos.net/spin',endpoint )

        _logger.info('Spin POS Terminal CALL on: %s', url)

        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            error_details = response.json()
            _logger.exception("SPIN-POS-ERROR \n %s", error_details)
            if silent:
                return error_details
            else:
                raise ValidationError("Spin: \n %s" % error_details)
        except requests.exceptions.RequestException as e:
            _logger.exception("unable to communicate with Mollie: %s \n %s", url, e)
            if silent:
                return {'error': "Some thing went wrong"}
            else:
                raise ValidationError("Spin: " + _("Some thing went wrong."))
        return response.json()

