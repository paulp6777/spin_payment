-- disable asiapay payment provider
UPDATE payment_provider
   SET ssl_merchant_id = NULL,
       ssl_user_id = NULL,
       ssl_pin = NULL;
       partner_code= NULL;
