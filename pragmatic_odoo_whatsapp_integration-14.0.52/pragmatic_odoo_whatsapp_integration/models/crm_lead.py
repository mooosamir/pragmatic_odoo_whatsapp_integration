# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
import requests
import json
from odoo.exceptions import UserError
import re
import logging
_logger = logging.getLogger(__name__)


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        res = super(CRMLead, self).create(vals)
        try:
            res.send_message_on_whatsapp()
        except Exception as e_log:
            _logger.exception("Exception in creating lead  %s:\n", str(e_log))
        return res

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def convert_to_html(self, message):
        for data in re.findall(r'\*.*?\*', message):
            message = message.replace(data, "<strong>" + data.strip('*') + "</strong>")
        return message

    def send_message_on_whatsapp(self):
        Param = self.env['res.config.settings'].sudo().get_values()
        res_partner_id = self.env['res.partner'].search([('id', '=', self.user_id.partner_id.id)])
        res_user_id = self.env['res.users'].search([('id', '=', self.env.user.id)])
        msg = ''
        whatsapp_msg_number = res_partner_id.mobile
        if whatsapp_msg_number:
            whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                '+' + str(res_partner_id.country_id.phone_code), "")
            if res_partner_id.country_id.phone_code and res_partner_id.mobile:
                if self.partner_id:
                    msg += "\n*" + _("Customer") + ':* ' + self.partner_id.name
                if self.email_from:
                    msg += '\n*' + _("Email") + ':* '+self.email_from
                if self.phone:
                    msg += '\n*' + _("Phone") + ':* '+self.phone
                if self.date_deadline:
                    msg += '\n*' + _("Expected closing date") + ':* '+str(self.date_deadline)
                if self.description:
                    msg += '\n*' + _("Description") + ':* ' +str(self.description)
                msg = _('Hello') + ' ' + res_partner_id.name+','+ '\n' + _("New lead assigned to you") + '\n*' + _("Lead name") + ':* '+self.name+""+msg
                if res_user_id:
                    if res_user_id.has_group('pragmatic_odoo_whatsapp_integration.group_crm_enable_signature'):
                        user_signature = self.cleanhtml(res_user_id.signature)
                        msg += "\n\n" + user_signature
                url = Param.get('whatsapp_endpoint') + '/sendMessage?token=' + Param.get('whatsapp_token')
                headers = {"Content-Type": "application/json"}
                tmp_dict = {
                    "phone": str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                    "body": msg
                }
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    json_send_message_response = json.loads(response.text)
                    if not json_send_message_response.get('sent') and json_send_message_response.get('error') and json_send_message_response.get(
                            'error').get('message') == 'Recipient is not a valid WhatsApp user':
                        raise UserError(_('Please add valid whatsapp number for %s ') % res_partner_id.name)
                    elif json_send_message_response.get('sent'):
                        _logger.info("\nSend Message successfully")
                        mail_message_obj = self.env['mail.message']
                        if self.env['ir.config_parameter'].sudo().get_param('pragmatic_odoo_whatsapp_integration.group_crm_display_chatter_message'):
                            comment = "fa fa-whatsapp"
                            body_html = tools.append_content_to_html('<div class = "%s"></div>' % tools.ustr(comment), msg)
                            body_msg = self.convert_to_html(body_html)
                            mail_message_id = mail_message_obj.sudo().create({
                                'res_id': self.id,
                                'model': 'crm.lead',
                                'body': body_msg,
                            })
            else:
                raise UserError(_('Please enter partner mobile number or select country for partner'))
