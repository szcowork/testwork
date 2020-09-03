odoo.define('einfo_code_manager.code_action', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var config = require('web.config');
    var core = require('web.core');
    var code_action = AbstractAction.extend({
        template: 'CodeGenerateAction',
        events: {
            'change .einfo_select': '_onChange',
            'click .einfo_code_button': 'on_einfo_code_button',
            'input .einfo_input': 'on_input_change',
            'click .einfo_code_generate': 'on_generate',
        },
         /**
         * @constructor
         */
        init:  function (parent, params) {
            this._super.apply(this, arguments);
            this.rule_id = params.context['rule_id']
            this.model_name = params.context.model_name
            this.field_name = params.context.field_name
            this.model_id = params.context.model_id
            this.sequence_rule_lines = []
        },
        /**
         * @override
         */
        start: function () {
            console.log(this)
            this._setValues()
            return this._super.apply(this, arguments);
        },
        einfo_render: function () {
            this.$el.empty();
            for (var i = 0; i < this.values.length; i++) {
                var temarray = this.values[i]
                if (temarray.ttype == 'select') {
                    var temdiv = $('<div style="flex-grow: 1; margin-right: 2px;">' +
                        '<h4 class="einfo_code">?</h4><select id="selectID" class="o_input einfo_select" ></select>' +
                        '<span>' + temarray.name + '</span></div>')
                    var tem_data = temarray.data
                    temdiv.find('select').append($('<option/>', {
                        value: '',
                        text: ''
                    }));
                    for (var j = 0; j < tem_data.length; j++) {
                        temdiv.find('select').append($('<option/>', {
                            value: JSON.stringify(tem_data[j][0]),
                            text: tem_data[j][1]
                        }));
                    }
                    this.$el.append(temdiv)
                }
                if (temarray.ttype == 'sequence') {
                    var temdiv = $('<div style="flex-grow: 1; margin-right: 2px;"><h4 class="einfo_code">?</h4>' +
                        '<div><button class="btn btn-primary einfo_code_button" data-id="' + temarray.data + '" type="button"  style="width:100%;padding-bottom: 2px;padding-top: 3px;">获取</button></div>' +
                        '<span>' + temarray.name + '</span></div>')
                    this.$el.append(temdiv)
                }
                if (temarray.ttype == 'char') {
                    var temdiv = $('<div style="flex-grow: 1; margin-right: 2px;"><h4 class="einfo_code">?</h4>' +
                        '<input class="o_field_char o_field_widget o_input einfo_input" name="name" placeholder="" type="text" >' +
                        '<span>' + temarray.name + '</span></div>')
                    this.$el.append(temdiv)
                }
            }
            this.$el.append($('<div style="flex-grow: 1; margin-right: 2px;"><h4 class="">&nbsp;</h4><button class="btn btn-primary einfo_code_generate" type="button"  style="padding-bottom: 2px;padding-top: 3px;">生成</button></div>'))
        },
        _setValues: function () {
            var self = this
            this.values = []
            this._rpc({
                model: 'einfo.code.rule',
                method: 'get_rule_data',
                args: [this.rule_id],
            }).then(function (result) {
                self.values = result
                // console.log(result)
                self.einfo_render()
            })
        },
        /**
         * @override
         */
        destroy: function () {
            this._super.apply(this, arguments);
        },
        _onChange: function (ev) {
            var value = JSON.parse(ev.target.value);
            ev.target.parentElement.firstChild.innerHTML = value
        },
        on_einfo_code_button: function (ev) {
            var sequence_rule_line = ev.target.getAttribute("data-id")
            if (this.sequence_rule_lines.includes(sequence_rule_line) == false) {
                this.sequence_rule_lines.push(parseInt(sequence_rule_line))
            }
            this._rpc({
                model: 'einfo.code.rule',
                method: 'get_sequence',
                args: [ev.target.getAttribute("data-id")],
            }).then(function (result) {
                ev.target.parentElement.parentElement.firstChild.innerHTML = result
            })
        },
        on_input_change: function (ev) {
            ev.target.parentElement.firstChild.innerHTML = ev.target.value
        },
        on_generate: function (ev) {
            var code_list = $('.einfo_code')
            var code = ''
            for (let index = 0; index < code_list.length; index++) {
                const element = code_list[index];
                code = code + element.innerHTML
            }
            var self = this
            this._rpc({
                model: 'einfo.code.rule',
                method: 'generate_code_client_action',
                args: [self.rule_id, code, self.model_name,self.model_id,self.field_name,self.sequence_rule_lines ],
            }).then(function (result) {
                console.log(result)
                self.do_action({ effect: false, type: 'ir.actions.act_window_close' });
            })
        },
    })

    core.action_registry.add('action_einfo_code', code_action);

    return code_action;
})