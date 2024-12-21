-- disable asiapay payment provider
UPDATE payment_provider
   SET app_id = NULL,
       secret_key = NULL,
     
