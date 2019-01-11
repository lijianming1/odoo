# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.addons.queue_job.job import job
import random


class TJMaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"
    _description = "机台"

    owner_worker_id = fields.Many2one('tj_maintenance.workers', string='包机人', track_visibility='onchange')
    periodic_maintenance_ids = fields.One2many('periodic.maintenance', 'equipment_id', '定期维护')
    equipment_parts_ids = fields.One2many('equipment.parts', 'equipment_id', '部件')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'maintenance.equipment')],
                                     string='附件')
    technical_phones = fields.Char('技术电话')
    purchase_person = fields.Char('采购人')
    purchase_phone = fields.Char('采购电话')
    approval_leader = fields.Char('审批领导')
    installation_date = fields.Datetime('安装时间')
    investment_date = fields.Datetime('投用时间')
    kb_num = fields.Char('机台号', default='JT001')
    kb_employ_num = fields.Char('当前员工号', default='TJ001')
    kb_running_state = fields.Char('运行状态', default='正常')
    kb_production_type = fields.Char('生产类型', default='None')
    kb_work_date = fields.Char('持续工作时间', default='None')
    kb_device_utilization = fields.Float('设备利用率', default='0')
    kb_production_qty = fields.Float('生产数量/米数', default='0')

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

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', index=True, required=False)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'maintenance.request')],
                                     string='附件')
    equipment_parts_ids = fields.Many2many('equipment.parts', string='机台部件')
    equipment_serial = fields.Char("机台序列", related='equipment_id.serial_no')
    equipment_model = fields.Char("机台型号", related='equipment_id.model')
    owner_worker_id = fields.Many2one('tj_maintenance.workers', default=False)
    owner_worker_num = fields.Char("工号", related='owner_worker_id.workernumber', stored=1, readonly=1)
    owner_worker_team = fields.Char("工种", compute='add_teamname_id', readonly=1 )
    receiving_worker_id = fields.Many2one('tj_maintenance.workers')
    receiving_worker_num = fields.Char("工号", related='receiving_worker_id.workernumber', stored=1, readonly=1)
    receiving_worker_team = fields.Char("工种", compute='add_teamname_id2', readonly=1)
    fault_cause_analysis = fields.Text("故障原因分析")
    receiving_date = fields.Datetime("接收时间")
    fault_type_ids = fields.Many2many('fault.type', string='故障类型')
    handelway_ids = fields.Many2many('maintenance.type', string="维护方法")
    receiving_description = fields.Text("维修方备注")
    maintenance_team_id = fields.Many2one('maintenance.team', string="指派工种", required=False)
    technician_worker_id = fields.Many2one('tj_maintenance.workers', string='指派人')
    parts_consume_ids = fields.One2many('parts.consume', 'maintenance_request_id')
    color = fields.Integer("Color Index")

    @api.one
    @api.depends('owner_worker_id')
    def add_teamname_id(self):
        self.owner_worker_team = ' '.join(self.owner_worker_id.teamname_ids.mapped('name'))

    @api.multi
    @api.depends('receiving_worker_id')
    def add_teamname_id2(self):
        add_teamname = ''
        for i in self:
            for j in i.receiving_worker_id.teamname_ids:
                add_teamname = add_teamname + ' ' + j.name
        i.receiving_worker_team = add_teamname

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
    equipment_id = fields.Many2one('maintenance.equipment', '机台' )
    name = fields.Char('部件名称')
    name_serial = fields.Char('部件类别编号')
    parts_type = fields.Char('部件型号')
    parts_parameter = fields.Char('技术参数')
    parts_suppliers = fields.Char('供应商')
    parts_stock_balance = fields.Integer('库存数量')
    notes = fields.Text('备注')


class FaulType(models.Model):
    _name = "fault.type"
    _description = "故障类型"

    name = fields.Char('故障类型名称')

class ProcessingWay(models.Model):
    _name = "processing.way"
    _description = "处理方式"

    name = fields.Char('处理方式名称')


class MonitoringConfiguration(models.Model):
    _name = "monitoring.configuration"
    _description = "监测配置"

    equipment_part_id = fields.Many2one('equipment.parts','机台部件')
    equipment_id = fields.Many2one('maintenance.equipment','机台',related='equipment_part_id.maintenance_equipment_id')
    equipment_serial = fields.Char('机台序列',related='equipment_id.serial_no')
    monitor_type = fields.Selection([('voltage', '电压'), ('current', '电流'),('thermal', '温度'), ('wire_diameter', '线径')], string="监测类型")
    Threshold_upper_limit = fields.Float(string='阈值上限', digits=dp.get_precision('Unit of Measure'))
    threshold_lower_limit = fields.Float(string='阈值下限', digits=dp.get_precision('Unit of Measure'))
    note = fields.Text('备注：')
    enable = fields.Boolean('使能')
    alarm_status = fields.Integer('报警状态(条)')
    is_confirm = fields.Boolean('确认',default=False)

    @api.multi
    def open_chart_monitoring_report(self):
        monitor_type_dict = {'voltage':'电压','current':'电流','thermal': '温度', 'wire_diameter': '线径'}
        data = {'equipment_part': self.equipment_part_id.name, 'equipment': self.equipment_id.name,
                'equipment_serial': self.equipment_serial, 'monitor_type': monitor_type_dict[self.monitor_type],
                'Threshold_upper_limit': self.Threshold_upper_limit,
                'threshold_lower_limit': self.threshold_lower_limit, 'note': self.note or None}
        return {
            'type': 'chart_monitoring_report',
            'data': data,
        }

class PartsConsume(models.Model):
    _name = "parts.consume"
    _description = "部件消耗"
    _order = "create_date desc"

    maintenance_request_id = fields.Many2one('maintenance.request')
    name_id = fields.Many2one('equipment.parts', '消耗件名称')
    parts_type = fields.Char('部件型号', related='name_id.parts_type')
    parts_parameter = fields.Char('技术参数', related='name_id.parts_parameter')
    parts_consume_mum = fields.Integer('消耗数量', default=1)


class MaintenanceType(models.Model):
    _name = "maintenance.type"
    _description = "维护方法"

    name = fields.Char('维护方法')
    color = fields.Integer("Color Index")

class PeriodicMaintenance(models.Model):
    _name = "periodic.maintenance"
    _description = "定期维修"

    name = fields.Char('Subjects', required=False)
    periodic_equipment_parts_ids = fields.Many2many('equipment.parts', string='机台部件', index=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='机台名称')
    equipment_serial = fields.Char('机台序列', related='equipment_id.serial_no')
    equipment_model = fields.Char('机台型号', related='equipment_id.model')
    maintenance_type_id = fields.Many2one('maintenance.type', "维护类型")
    maintenance_duration = fields.Float(digits=(4, 1), string='维护周期/天')
    maintenance_start_date = fields.Datetime(string='维护起始日期', default=fields.Datetime.now)
    recent_maintenance_date = fields.Datetime(string='上次维护日期')
    next_maintenance_date = fields.Datetime(string='下次维护日期', readonly=False)
    owner_worker = fields.Char("包机人", related='equipment_id.owner_worker_id.name')
    maintenance_description = fields.Text("定期维护备注")
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='优先级')
    color = fields.Integer("Color Index")
    maintenance_repaire_plan_duration = fields.Float(digits=(3, 1), help="Maintenance Duration in hours.", string="计划维修耗时")
    def _create_new_periodic_request(self):
        self.ensure_one()
        self.env['maintenance.request'].create({
            'equipment_id': self.equipment_id.id,
            'equipment_serial': self.equipment_serial,
            'equipment_parts_ids': self.periodic_equipment_parts_ids,
            'owner_worker_id': 1,
            'owner_worker_num': 000,
            'owner_worker_team': "全部",
            'duration': self.maintenance_repaire_plan_duration
        })

    @api.model
    def _cron_generate_requests2(self):
        for equipment in self.search([('maintenance_duration', '>', 0)]):
            next_requests = self.env['maintenance.request'].search([('stage_id.done', '=', False),
                                                                    ('equipment_id', '=', self.equipment_id.id),
                                                                    ('owner_worker_id', '=', 1),
                                                                    ('create_date', '<=', (fields.Datetime.from_string(
                                                                        equipment.next_maintenance_date)
                                                                                           - timedelta(
                                                                                seconds=120)).strftime(
                                                                        "%Y-%m-%d %H:%M:%S")),
                                                                    ('create_date', '>=', (fields.Datetime.from_string(
                                                                        equipment.next_maintenance_date)
                                                                                           - timedelta(
                                                                                seconds=120)).strftime(
                                                                     "%Y-%m-%d %H:%M:%S")), ])
            if not next_requests:
                if datetime.now().strftime("%Y-%m-%d") >= (fields.Datetime.from_string(equipment.next_maintenance_date)
                ).strftime("%Y-%m-%d"):
                    equipment._create_new_periodic_request()
                    equipment.recent_maintenance_date = datetime.now()
                    equipment.next_maintenance_date = fields.Datetime.from_string(equipment.recent_maintenance_date) + \
                                                      timedelta(equipment.maintenance_duration)

    @api.onchange('maintenance_start_date', 'maintenance_start_date')
    def _compute_next_maintenance_date(self):
        for r in self:
            if (r.maintenance_start_date and r.maintenance_duration):
                r.next_maintenance_date = timedelta(r.maintenance_duration) + fields.Datetime.from_string(
                    r.maintenance_start_date)

class TJUsers(models.Model):
    _name = "tj_maintenance.workers"
    _description = "用户"

    name = fields.Char("员工")
    workernumber = fields.Char("工号")
    teamname_ids = fields.Many2many('maintenance.team', string='工种')
    phone = fields.Char("手机")
    _sql_constraints = [
        ('workernumber', 'unique(workernumber)', "工号不能重复，请改成其他工号!"),
    ]

