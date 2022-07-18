# -*- coding: utf-8 -*-
"""
    This file is used for create and inherit the core controllers
"""
import datetime
import json
import logging
from werkzeug.exceptions import NotFound
from odoo.http import request
from odoo import fields, http
from odoo.addons.website.controllers.main import Website
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.addons.sale.controllers.variant import VariantController
from odoo.addons.website_sale_wishlist.controllers.main import WebsiteSaleWishlist
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSaleExt(WebsiteSale):

    # b2b cart process
    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, access_token=None, revive='', **post):
        """
        inherited to check for b2b option for public user
        @return: super object
        """
        if request.website.b2b_hide_details and request.website.is_public_user():
            return request.redirect('/', code=301)
        return super(WebsiteSaleExt, self).cart(access_token=access_token, revive=revive, **post)

    @http.route(['/shop/clear_cart'], type='json', auth="public", website=True)
    def clear_cart(self):
        """
        Clear the cart in e-commerce website
        @return: -
        """
        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                line.unlink()

    # checkout controller - inherit for give option for b2b chekout configuration
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        """
        inherited controller for b2b checkout functionality
        @param post: arguments
        @return: super
        """
        login_url = '/web/login'
        redirect_url = f'{login_url}?redirect={request.httprequest.url}'
        if request.website.b2b_checkout and request.website.is_public_user():
            return request.redirect(redirect_url, code=301)
        res = super(WebsiteSaleExt, self).checkout(**post)
        return res


class EmiproThemeBase(http.Controller):

    @http.route(['/get_banner_video_data'], type='json', auth="public", website=True)
    def get_banner_video_data(self, is_ios):
        """
        get data for banner video
        @param is_ios: check for system
        @return: http response
        """
        template = request.env['ir.ui.view'].sudo().search([('key', '=', 'theme_clarico_vega.banner_video_template')])
        if template:
            values = {
                'banner_video_url': request.website.banner_video_url or False,
                'is_ios': is_ios,
            }
            response = http.Response(template="theme_clarico_vega.banner_video_template", qcontext=values)
            return response.render()

    @http.route(['/mega_menu_content_dynamic'], type='json', auth="public", website=True)
    def mega_menu_content_dynamic(self, menu_id):
        """
        get mega menu content
        @param menu_id: record of website.menu
        @return: http response
        """
        response = http.Response(template="emipro_theme_base.website_dynamic_category")
        current_menu = request.env['website.menu'].sudo().search([('id', '=', menu_id)])
        if current_menu.is_dynamic_menu and current_menu.mega_menu_content_dynamic != response.render().decode():
            current_menu.write({
                "mega_menu_content_dynamic": response.render().decode(),
                "is_dynamic_menu_json": False
            })
            return response.render().decode()
        return False

    @http.route(['/dynamic_mega_menu_child'], type='json', auth="public", website=True)
    def dynamic_mega_menu_child(self, category_id):
        """
        dynamic meda menu for category
        @param category_id: record for category_id
        @return: http response
        """
        current_category = request.env['product.public.category'].sudo().search([('id', '=', category_id)])
        if current_category:
            values = {
                'current_menu': current_category.id,
                'child_ids': current_category.child_id,
            }
            response = http.Response(template="emipro_theme_base.dynamic_mega_menu_child", qcontext=values)
            return response.render()

    @http.route(['/dynamic_category_mega_menu'], type='json', auth="public", website=True)
    def dynamic_category_mega_menu(self, menu_id):
        """
        This controller return the template for Dynamic Mega Menu with required details
        :param menu_id: get current menu id
        :return: dynamic mega menu template html
        """
        current_menu = request.env['website.menu'].sudo().search([('id', '=', menu_id)])
        if current_menu.dynamic_mega_menu:
            current_category_menu_style = current_menu.category_menu_styles
            if current_category_menu_style:
                values = {
                    'parent_menu': current_menu,
                    'category_menu_styles': current_category_menu_style
                }
                response = http.Response(template="emipro_theme_base.dynamic_category_mega_menu",
                                         qcontext=values)
                return response.render()

    @http.route(['/quick_view_item_data'], type='json', auth="public", website=True)
    def get_quick_view_item(self, product_id=None):
        """
        This controller return the template for QuickView with product details
        :param product_id: get product id
        :return: quick_view template html
        """
        if product_id:
            product = request.env['product.template'].search([['id', '=', product_id]])
            values = {
                'product': product,
            }
            response = http.Response(template="emipro_theme_base.quick_view_container", qcontext=values)
            return response.render()

    @http.route(['/shop/cart/update_custom'], type='json', auth="public", methods=['GET', 'POST'], website=True,
                csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, product_custom_attribute_values=None, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        # product_custom_attribute_values = None
        if product_custom_attribute_values:
            product_custom_attribute_values = json.loads(product_custom_attribute_values)

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        if sale_order:
            sale_order._cart_update(
                product_id=int(product_id),
                add_qty=add_qty,
                set_qty=set_qty,
                product_custom_attribute_values=product_custom_attribute_values,
                no_variant_attribute_values=no_variant_attribute_values,
                )
            return True
        return False

    @http.route(['/ajax_cart_item_data'], type='json', auth="public", website=True)
    def get_ajax_cart_item(self, product_id=None):
        """
        This controller return the template for Ajax Add to Cart with product details
        :param product_id: get product id
        :return: ajax cart template for variants html
        """
        if product_id:
            product = request.env['product.template'].search([['id', '=', product_id]])
            values = {
                'product': product,
            }
            response = http.Response(template="emipro_theme_base.ajax_cart_container", qcontext=values)
            return response.render()

    @http.route(['/ajax_cart_sucess_data'], type='json', auth="public", website=True)
    def get_ajax_cart_sucess(self, product_id=None, product_product=None):
        """
        This controller return the template for Ajax Add to Cart with product details
        :param product_id: get product id
        :return: ajax cart template for success html
        """
        if product_id:
            product = request.env['product.template'].search([['id', '=', product_id]])
            product_variant = request.env['product.product'].search([['id', '=', product_product]])
            values = {
                'product': product,
                'product_variant': product_variant,
            }
            response = http.Response(template="emipro_theme_base.ajax_cart_success_container", qcontext=values)
            return response.render()

    @http.route(['/brands'], type='http', auth="public", website=True)
    def brands(self):
        """
        render product brands
        @return: render template
        """
        return request.render('theme_clarico_vega.brand_listing_template')

    @http.route(['/brand-listing'], type='http', auth="public", website=True)
    def brand_listing(self):
        """
        render brand page
        """
        return request.redirect('/brands')

    @http.route('/order_reorder', type='json', auth="public", website=True)
    def reorder_sales_order(self, order_id):
        """ Update products to cart when a user clicks reorder button and redirect user to cart"""
        old_sale_order = request.env['sale.order'].sudo().browse(int(order_id))
        new_sale_order = request.website.sale_get_order(force_create=True)
        if new_sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            new_sale_order = request.website.sale_get_order(force_create=True)
        order_lines = []
        for line1 in old_sale_order.order_line:
            flag = False
            if new_sale_order.order_line:
                for line2 in new_sale_order.order_line:
                    if line1.product_id == line2.product_id:
                        line2.product_uom_qty = line1.product_uom_qty + line2.product_uom_qty
                        flag = True
                        break
                if not flag:
                    order_lines.append(line1)
            else:
                order_lines.append(line1)
        for order_line in old_sale_order.mapped('order_line'):
            new_sale_order._cart_update(product_id=order_line.product_id.id,
                                        add_qty=order_line.product_uom_qty)
        response = http.Response()
        return response.render()

    @http.route(['/order_check_reorder'], type='json', auth="public", website=True)
    def _check_product_stock(self, order_id=None):
        """ This controller will check stock of all products of a sales order
            return: True if all products have enough stock else False
        """
        if order_id:
            sale_order = request.env['sale.order'].sudo().browse(int(order_id))

            display_popup = False
            for line1 in sale_order.order_line:
                if not line1.product_id.allow_out_of_stock_order and line1.product_id.detailed_type == 'product' \
                        and line1.product_uom_qty > line1.product_id.qty_available:
                    display_popup = True
                    break
            return display_popup


class EmiproThemeBaseExtended(WebsiteSaleWishlist):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        """
        Inherit method for implement Price Filter and Brand Filter
        :param search:
        :param category:
        :param attrib_values:
        :return: search domain
        """

        domain = super(EmiproThemeBaseExtended, self)._get_search_domain(
            search=search, category=category, attrib_values=attrib_values, search_in_description=search_in_description)
        cust_min_val = request.httprequest.values.get('min_price', False)
        cust_max_val = request.httprequest.values.get('max_price', False)

        if cust_max_val and cust_min_val:
            try:
                cust_max_val = float(cust_max_val)
                cust_min_val = float(cust_min_val)
            except ValueError:
                raise NotFound()
            products = request.env['product.template'].sudo().search(domain)
            new_prod_ids = []
            pricelist = request.website.pricelist_id
            # return the product ids as per option selected (sale price or discounted price)
            if products:
                if request.website.price_filter_on == 'website_price':
                    context = dict(request.context, quantity=1, pricelist=pricelist.id if pricelist else False)
                    products = products.with_context(context)
                    new_prod_ids = products.filtered(
                        lambda r: r.price >= float(cust_min_val) and r.price <= float(cust_max_val)).ids
                else:
                    new_prod_ids = products.filtered(
                        lambda r: r.currency_id._convert(
                            r.list_price, pricelist.currency_id,
                            request.website.company_id, date=fields.Date.today()) >= float(cust_min_val) and
                                  r.currency_id._convert(
                                      r.list_price, pricelist.currency_id, request.website.company_id,
                                      date=fields.Date.today()) <= float(cust_max_val)).ids
                domain += [('id', 'in', new_prod_ids)]
            else:
                domain = [('id', '=', False)]
        if attrib_values:
            ids = []
            # brand Filter
            for value in attrib_values:
                if value[0] == 0:
                    ids.append(value[1])
                    domain += [('product_brand_ept_id.id', 'in', ids)]
        return domain

    @http.route('/hover/color', type='json', auth="public", methods=['POST'], website=True)
    def on_color_hover(self, color_id='', product_id='', hover=False):
        """
        veriant color hover
        @param color_id: attrubute of color type
        @param product_id: product_id
        @param hover: Boolean
        @return: product image src path
        """
        product = request.env['product.template'].browse(int(product_id))
        if hover:
            variant = product.product_variant_ids.filtered(
                lambda p: int(color_id) in p.product_template_variant_value_ids.product_attribute_value_id.ids)[0]
            return '/web/image/product.product/'+str(variant.id)+'/image_512'
        return '/web/image/product.template/' + product_id + '/image_512'


class EptWebsiteSaleVariantController(VariantController):
    """
    Class for Variant color process
    """

    @http.route(['/sale/get_combination_info_website'], type='json', auth="public", methods=['POST'],
                website=True)
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, **kw):
        """
        Inherit this method because set the product offer timer data if it's available
        :return: result
        """

        res = super(EptWebsiteSaleVariantController, self).get_combination_info_website(
            product_template_id=product_template_id,
            product_id=product_id,
            combination=combination,
            add_qty=add_qty, **kw)
        product = request.env['product.product'].sudo().search([('id', '=', res.get('product_id'))])
        partner = request.env['res.users'].sudo().search([('id', '=', request.uid)]).partner_id
        products_qty_partner = []
        products_qty_partner.append((product, add_qty, partner))
        pricelist = request.website.get_current_pricelist()
        suitable_rule = False
        res.update({'is_offer': False})
        # set internal reference
        product_temp = request.env['product.template'].sudo().search([('id', '=', product_template_id)])
        res.update({
            'sku_details': product.default_code if product_temp.product_variant_count > 1 else product_temp.default_code
        })
        try:
            if pricelist and product:
                vals = pricelist._compute_price_rule(products_qty_partner)
                if vals.get(int(product)) and vals.get(int(product))[1]:
                    suitable_rule = vals.get(int(product))[1]
                    suitable_rule = request.env['product.pricelist.item'].sudo().search(
                        [('id', '=', suitable_rule), ('is_display_timer', '=', True)])
                    if suitable_rule.date_end and (
                            suitable_rule.applied_on == '3_global' or
                            suitable_rule.product_id or suitable_rule.product_tmpl_id or suitable_rule.categ_id):
                        start_date = int(round(datetime.datetime.timestamp(suitable_rule.date_start) * 1000))
                        end_date = int(round(datetime.datetime.timestamp(suitable_rule.date_end) * 1000))
                        current_date = int(round(datetime.datetime.timestamp(datetime.datetime.now()) * 1000))
                        res.update({'is_offer': True,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'current_date': current_date,
                                    'suitable_rule': suitable_rule,
                                    'offer_msg': suitable_rule.offer_msg,
                                    })
        except Exception as e:
            return res
        return res


class WebsiteExt(Website):
    """
    Class for Website Inherit
    """

    @http.route(website=True, auth="public", sitemap=False, csrf=False)
    def web_login(self, *args, **kw):
        """
            Login - overwrite of the web login so that regular users are redirected to the backend
            while portal users are redirected to the same page from popup
            Returns formatted data required by login popup in a JSON compatible format
        """
        login_form_ept = kw.get('login_form_ept', False)
        if kw.get('login_form_ept', False):
            kw.pop('login_form_ept')
        response = super(WebsiteExt, self).web_login(*args, **kw)
        if login_form_ept:
            if response.is_qweb and response.qcontext.get('error', False):
                return json.dumps(
                    {'error': response.qcontext.get('error', False), 'login_success': False, 'hide_msg': False})
            else:
                if request.params.get('login_success', False):
                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])
                    user = request.env['res.users'].browse(uid)
                    redirect = '1'
                    if user.totp_enabled:
                        redirect = request.env(user=uid)['res.users'].browse(uid)._mfa_url()
                        return json.dumps({'redirect': redirect, 'login_success': True, 'hide_msg': True})
                    if user.has_group('base.group_user'):
                        redirect = b'/web?' + request.httprequest.query_string
                        redirect = redirect.decode('utf-8')
                    return json.dumps({'redirect': redirect, 'login_success': True, 'hide_msg': False})
        return response


class AuthSignupHome(Home):

    @http.route(website=True, auth="public", sitemap=False, csrf=False)
    def web_auth_signup(self, *args, **kw):
        """
            Signup from popup and redirect to the same page
            Returns formatted data required by login popup in a JSON compatible format
        """
        signup_form_ept = kw.get('signup_form_ept', False)
        if kw.get('signup_form_ept', False):
            kw.pop('signup_form_ept')
        response = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
        if signup_form_ept:
            if response.is_qweb and response.qcontext.get('error', False):
                return json.dumps({'error': response.qcontext.get('error', False), 'login_success': False})
            else:
                if request.params.get('login_success', False):
                    redirect = '1'
                    return json.dumps({'redirect': redirect, 'login_success': True})
        return response

    @http.route(auth='public', website=True, sitemap=False, csrf=False)
    def web_auth_reset_password(self, *args, **kw):
        """
            Reset password from popup and redirect to the same page
            Returns formatted data required by login popup in a JSON compatible format
        """
        reset_form_ept = kw.get('reset_form_ept', False)
        if kw.get('reset_form_ept', False):
            kw.pop('reset_form_ept')
        response = super(AuthSignupHome, self).web_auth_reset_password(*args, **kw)
        if reset_form_ept:
            if response.is_qweb and response.qcontext.get('error', False):
                return json.dumps({'error': response.qcontext.get('error', False)})
            elif response.is_qweb and response.qcontext.get('message', False):
                return json.dumps({'message': response.qcontext.get('message', False)})
        return response
