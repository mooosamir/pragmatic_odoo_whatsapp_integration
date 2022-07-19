from odoo import api, fields, models, _


class base(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_endpoint = fields.Char('Whatsapp Endpoint', help="Whatsapp api endpoint url with instance id")
    whatsapp_token = fields.Char('Whatsapp Token')

    @api.model
    def get_values(self):
        res = super(base, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        res['whatsapp_endpoint'] = param.sudo().get_param('pragtech_whatsapp_base.whatsapp_endpoint')
        res['whatsapp_token'] = param.sudo().get_param('pragtech_whatsapp_base.whatsapp_token')
        return res

    def set_values(self):
        super(base, self).set_values()
        if self.whatsapp_endpoint:
            if (self.whatsapp_endpoint)[-1] == '/':
                self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_base.whatsapp_endpoint',
                                                                 (self.whatsapp_endpoint)[:-1])
            else:
                self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_base.whatsapp_endpoint', self.whatsapp_endpoint)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_base.whatsapp_token', self.whatsapp_token)
