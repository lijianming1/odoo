# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons.queue_job.job import job

class TJMaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"
    _description = "机台"

    equipment_parts_ids = fields.One2many('equipment.parts', 'maintenance_equipment_id', '部件')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'maintenance.equipment')], string='附件')

    @api.multi
    def action_get_attachment_view(self):
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'maintenance.equipment'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'maintenance.equipment', 'default_res_id': self.id}
        return res


class TJMaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    _description = "维护申请"

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'maintenance.request')],string='附件')
    equipment_parts_id = fields.Many2one('equipment.parts','部件')

    @api.multi
    def action_get_attachment_view(self):
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'maintenance.request'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'maintenance.request', 'default_res_id': self.id}
        return res

class EquipmentParts(models.Model):
    _name = "equipment.parts"
    _description = "设备部位"

    name = fields.Char('设备部位名称')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment','机台')
