# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).


from odoo import _, http

class EChartsController(http.Controller):

    @http.route('/web/monitoring_chart', type='json', auth='user')
    def monitoring_chart(self, data):
        context = data
        return context