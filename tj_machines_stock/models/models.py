# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TJ_Machines_Stock(models.Model):
    _name = 'tj_machines.stock'
    _description = '部件库存'

#     name = fields.Char("货物名称")
#     categories = fields.Char("类别编号")
#     count = fields.Integer('数量')
#     currency_id = fields.Many2one('res.currency', string='Currency')
#     per_price = fields.Monetary('金额', currency_field='currency_id',)
#     supplier_name = fields.Char('供应商名称')
#     supplier_tel = fields.Char('手机')
#     where_to_use = fields.Char('使用地点')
#     stock_place_id = fields.Many2one('tj_stock.shelves', "存放货架",)
#     stock_layers_id = fields.Many2one('tj_shelves.layers', '存放层')
#     purchase_date = fields.Datetime("采购日期")
#     receiver_id = fields.Many2one('tj_maintenance.workers', "收货人")
#     receiver_num = fields.Char("工号", related='receiver_id.')
#
#
# class TJ_Stock_Shelves(models.Model):
#     _name = 'tj_stock.shelves'
#     _description = '存货架'
#
#     name = fields.Char('货架编号')
#     name_description = fields.Char('货架注释')
#     machines_stock_ids = fields.One2many('tj_machines.stock', 'stock_place_id', string='部件库存', )
#
#
# class TJ_Shelves_layers(models.Model):
#     _name = 'tj_shelves.layers'
#     _description = '货架层'
#
#     name = fields.Char('货架层编号')
#     name_description = fields.Char('货架注释')
#
#
# class tj_machines_stock(models.Model):
#     _name = 'tj_machines_stock.tj_machines_stock'
#
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100