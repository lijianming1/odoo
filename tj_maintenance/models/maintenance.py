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
    technical_phones = fields.Char('技术电话')
    purchase_person= fields.Char('采购人')
    purchase_phone = fields.Char('采购电话')
    approval_leader = fields.Char('审批领导')
    installation_date = fields.Datetime('安装时间')
    investment_date = fields.Datetime('投用时间')
    kb_num = fields.Char('机台号')
    kb_employ_num = fields.Char('当前员工号')
    kb_running_state = fields.Char('运行状态')
    kb_production_type = fields.Char('生产类型')
    kb_work_date = fields.Datetime('持续工作时间')
    kb_device_utilization = fields.Float('设备利用率')
    kb_production_qty = fields.Float('生产数量/米数')

    @api.multi
    def action_get_attachment_view(self):
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'maintenance.equipment'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'maintenance.equipment', 'default_res_id': self.id}
        return res


class TJMaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    _description = "维护申请"

    name = fields.Char(required=False)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'maintenance.request')],string='附件')
    equipment_parts_id = fields.Many2one('equipment.parts', '设备部位')
    equipment_serial = fields.Char("设备序列", related='equipment_id.serial_no')
    owner_user_num = fields.Char("工号")
    owner_user_team_id = fields.Char("工种")
    owner_user_id = fields.Many2one('res.users', readonly=False, default=False)
    receiving_user = fields.Many2one('res.users')
    receiving_user_num = fields.Char("工号")
    receiving_user_team_id = fields.Char("工种")
    fault_cause_analysis = fields.Text("故障原因分析")
    receiving_date = fields.Datetime("接收时间")
    fault_type = fields.Many2one('fault.type', "故障类型")
    processing_way = fields.Many2one('processing.way', "处理方式")
    receiving_description = fields.Text("维修方备注")

    @api.multi
    def archive_submit_request(self):
        first_stage_obj = self.env['maintenance.stage'].search([], order="sequence asc", limit=2)
        self.write({'archive': False, 'stage_id': first_stage_obj[-1].id})

    @api.multi
    def reset_done_request(self):
        first_stage_obj = self.env['maintenance.stage'].search([], order="sequence asc", limit=3)
        self.write({'archive': False, 'stage_id': first_stage_obj[-1].id})

    @api.multi
    def write(self, vals):
        res = super(TJMaintenanceRequest, self).write(vals)
        if self.stage_id.sequence == 2 and 'stage_id' in vals:
            self.write({'receiving_date': fields.Datetime.now()})
        if self.stage_id.sequence == 1 and 'stage_id' in vals and self.receiving_date:
            raise UserError('正在进行的维护单不可重复提交！')
        return res

    @api.multi
    def action_get_attachment_view(self):
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'maintenance.request'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'maintenance.request', 'default_res_id': self.id}
        return res

class EquipmentParts(models.Model):
    _name = "equipment.parts"
    _description = "机台部件"

    name = fields.Char('机台部件名称')
    maintenance_equipment_id = fields.Many2one('maintenance.equipment','机台')
    parameters_1 = fields.Char('参数1')
    parameters_2 = fields.Char('参数2')
    parameters_3 = fields.Char('参数3')
    parameters_4 = fields.Char('参数4')
    parameters_5 = fields.Char('参数5')
    notes = fields.Text('备注')

class FaulType(models.Model):
    _name = "fault.type"
    _description = "故障类型"

    name = fields.Char('故障类型名称')

class ProcessingWay(models.Model):
    _name = "processing.way"
    _description = "处理方式"

    name = fields.Char('处理方式名称')