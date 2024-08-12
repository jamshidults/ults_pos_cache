# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import json
from ast import literal_eval

from odoo import models, fields, api
from odoo.tools import date_utils


class pos_cache(models.Model):
    _name = 'pos.cache'
    _description = 'Point of Sale Cache'

    cache = fields.Binary(attachment=True)
    product_domain = fields.Text(required=True)
    product_fields = fields.Text(required=True)



    @api.model
    def refresh_all_caches(self):
        self.env['pos.cache'].search([]).refresh_cache()

    def refresh_cache(self):
        for cache in self:
            Product = self.env['product.product']
            products = Product.search(cache.get_product_domain(), order='sequence,default_code,name')
            prod_ctx = products.with_context(display_default_code=False)
            res = prod_ctx.read(cache.get_product_fields())
            cache.write({
                'cache': base64.encodebytes(json.dumps(res, default=date_utils.json_default).encode('utf-8')),
            })

    @api.model
    def get_product_domain(self):
        return literal_eval(self.product_domain)

    @api.model
    def get_product_fields(self):
        return literal_eval(self.product_fields)

    def cache2json(self):
        return json.loads(base64.decodebytes(self.cache).decode('utf-8'))


class pos_config(models.Model):
    _inherit = 'pos.config'
    limit_products_per_request = fields.Integer(compute='_compute_limit_products_per_request')

    def _compute_limit_products_per_request(self):
        limit = self.env['ir.config_parameter'].sudo().get_param('pos_cache.limit_products_per_request', 0)
        self.update({'limit_products_per_request': int(limit)})


