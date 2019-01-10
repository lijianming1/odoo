/* Copyright 2018 Naglis Jonaitis
 * License LGPL-3 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('web.tj_maintenance', function (require) {
    'use strict';


    var ActionManager = require('web.ActionManager');
    var Dialog = require('web.Dialog');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    ActionManager.include({
        chart_monitoring_report: function (action) {
            var self = this;
            // console.log(action);
            var action = action;

            var dialog = new Dialog(
                this,
                _.extend({
                    $content: QWeb.render('Monitoring_Chart', {
                        data: action.data,
                        help_text: action.help_text,
                        flags: action.flags,
                    }),
                    size: action.size || 'large',
                    title: action.name || _t('结款情况'),
                    buttons: [
                        {
                            text: _t('Close'),
                            close: true
                        }
                    ],
                })
            );

            dialog.opened().then(function () {
                self._rpc({
                    route: '/web/monitoring_chart',
                    params: {
                        data: action.context
                    }
                }).then(function (result) {
                    // console.log(result);
                    var myChart = echarts.init(document.getElementById('chart-monitoring-report'));
                    var option = {
                        xAxis: {
                            type: 'category',
                            data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                        },
                        yAxis: {
                            type: 'value'
                        },
                        series: [{
                            data: [820, 932, 901, 934, 1290, 1330, 1320],
                            type: 'line',
                            smooth: true
                        }]
                    };
                    myChart.setOption(option);
                }).fail(function (error, event) {
                    event.preventDefault();
                }).always(function () {
                });
            });
            return dialog.open();

        },
    });

});
