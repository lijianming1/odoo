# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'TJ Manintenance',
    'version': '1.0',
    'category': 'Manintenance',
    'sequence': 15,
    'summary': '维护模块',
    'description': """
    1.维护\n
    """,
    'website': '',
    'depends': ['web','maintenance','decimal_precision'],
    'data': [
        'views/maintenance_views.xml',
        'views/templates.xml',
        # 'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/echarts_action.xml',
    ],
    'application': True,
    # 'uninstall_hook': 'uninstall_hook',
    # 'post_init_hook': 'post_init_hook',
}
