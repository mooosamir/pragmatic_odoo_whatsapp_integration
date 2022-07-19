import logging
import requests
import base64
import json
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class base(models.TransientModel):
    _inherit = "res.config.settings"

    group_enable_signature = fields.Boolean("Add Signature in so?", implied_group='pragmatic_odoo_whatsapp_integration.group_enable_signature')
    group_display_chatter_message = fields.Boolean("Add in chatter message so?",implied_group='pragmatic_odoo_whatsapp_integration.group_display_chatter_message')
    group_order_product_details_msg = fields.Boolean("Add Order product details in message so?",implied_group='pragmatic_odoo_whatsapp_integration.group_order_product_details_msg')
    group_order_info_msg = fields.Boolean("Add Order information in message so?",implied_group='pragmatic_odoo_whatsapp_integration.group_order_info_msg')

    group_purchase_enable_signature = fields.Boolean("Add Signature in po?", implied_group='pragmatic_odoo_whatsapp_integration.group_purchase_enable_signature')
    group_purchase_display_chatter_message = fields.Boolean("Add in chatter message po?", implied_group='pragmatic_odoo_whatsapp_integration.group_purchase_display_chatter_message')
    group_purchase_order_product_details_msg = fields.Boolean("Add Order product details in message po?",
                                                            implied_group='pragmatic_odoo_whatsapp_integration.group_purchase_order_product_details_msg')
    group_purchase_order_info_msg = fields.Boolean("Add Order information in message po?", implied_group='pragmatic_odoo_whatsapp_integration.group_purchase_order_info_msg')
    group_stock_enable_signature = fields.Boolean("Add Signature in do?", implied_group='pragmatic_odoo_whatsapp_integration.group_stock_enable_signature')
    group_stock_display_chatter_message = fields.Boolean("Add in chatter message do?",
                                                            implied_group='pragmatic_odoo_whatsapp_integration.group_stock_display_chatter_message')
    group_stock_product_details_msg = fields.Boolean("Add order product details in message do?",
                                                              implied_group='pragmatic_odoo_whatsapp_integration.group_stock_product_details_msg')
    group_stock_info_msg = fields.Boolean("Add order information in message do?", implied_group='pragmatic_odoo_whatsapp_integration.group_stock_info_msg')
    group_invoice_enable_signature = fields.Boolean("Add Signature in invoice?", implied_group='pragmatic_odoo_whatsapp_integration.group_invoice_enable_signature')
    group_invoice_display_chatter_message = fields.Boolean("Add in chatter message invoice?",
                                                         implied_group='pragmatic_odoo_whatsapp_integration.group_invoice_display_chatter_message')
    group_invoice_product_details_msg = fields.Boolean("Add order product details in message invoice?",
                                                     implied_group='pragmatic_odoo_whatsapp_integration.group_invoice_product_details_msg')
    group_invoice_info_msg = fields.Boolean("Add order information in message invoice?", implied_group='pragmatic_odoo_whatsapp_integration.group_invoice_info_msg')

    group_crm_display_chatter_message = fields.Boolean("Add in chatter message crm?",
                                                           implied_group='pragmatic_odoo_whatsapp_integration.group_crm_display_chatter_message')
    group_crm_enable_signature = fields.Boolean("Add Signature in crm?", implied_group='pragmatic_odoo_whatsapp_integration.group_crm_enable_signature')

    group_project_display_chatter_message = fields.Boolean("Add in chatter message in project?",
                                                       implied_group='pragmatic_odoo_whatsapp_integration.group_project_display_chatter_message')
    group_project_enable_signature = fields.Boolean("Add Signature in project?", implied_group='pragmatic_odoo_whatsapp_integration.group_project_enable_signature')

    @api.model
    def get_values(self):
        res = super(base, self).get_values()
        Param = self.env['ir.config_parameter'].sudo()
        res['group_enable_signature'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_enable_signature')
        res['group_display_chatter_message'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_display_chatter_message')
        res['group_order_product_details_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_order_product_details_msg')
        res['group_order_info_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_order_info_msg')
        res['group_purchase_enable_signature'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_purchase_enable_signature')
        res['group_purchase_display_chatter_message'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_purchase_display_chatter_message')
        res['group_purchase_order_product_details_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_purchase_order_product_details_msg')
        res['group_purchase_order_info_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_purchase_order_info_msg')
        res['group_stock_enable_signature'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_stock_enable_signature')
        res['group_stock_display_chatter_message'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_stock_display_chatter_message')
        res['group_stock_product_details_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_stock_product_details_msg')
        res['group_stock_info_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_stock_info_msg')
        res['group_invoice_enable_signature'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_invoice_enable_signature')
        res['group_invoice_display_chatter_message'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_invoice_display_chatter_message')
        res['group_invoice_product_details_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_invoice_product_details_msg')
        res['group_invoice_info_msg'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_invoice_info_msg')
        res['group_crm_enable_signature'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_crm_enable_signature')
        res['group_crm_display_chatter_message'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_crm_display_chatter_message')
        res['group_project_enable_signature'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_project_enable_signature')
        res['group_project_display_chatter_message'] = Param.sudo().get_param('pragmatic_odoo_whatsapp_integration.group_project_display_chatter_message')
        return res

    def set_values(self):
        super(base, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_enable_signature', self.group_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_display_chatter_message', self.group_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_order_product_details_msg', self.group_order_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_order_info_msg', self.group_order_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_purchase_enable_signature', self.group_purchase_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_purchase_display_chatter_message', self.group_purchase_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_purchase_order_product_details_msg', self.group_purchase_order_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_purchase_order_info_msg', self.group_purchase_order_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_stock_enable_signature', self.group_stock_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_stock_display_chatter_message', self.group_stock_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_stock_product_details_msg',
                                                         self.group_stock_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_stock_info_msg', self.group_stock_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_invoice_enable_signature', self.group_invoice_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_invoice_display_chatter_message', self.group_invoice_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_invoice_product_details_msg',
                                                         self.group_invoice_product_details_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_invoice_info_msg', self.group_invoice_info_msg)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_crm_enable_signature', self.group_crm_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_crm_display_chatter_message', self.group_crm_display_chatter_message)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_project_enable_signature', self.group_project_enable_signature)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_odoo_whatsapp_integration.group_project_display_chatter_message', self.group_project_display_chatter_message)

