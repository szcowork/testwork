odoo.define('einfo_code_manager.code_manager', function (require) {
    "use strict";
    var AbstractField = require('web.AbstractField');
    var basicFields = require('web.basic_fields');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var registry = require('web.field_registry');
    var _t = core._t;
    var qweb = core.qweb;
    var CodeGenerateArray = AbstractField.extend({
        template: 'CodeGenerate',
        supportedFieldTypes: ['char'],
        events: _.extend({}, AbstractField.prototype.events, {
            'change .einfo_select': '_onChange',
            'click .einfo_code_button': 'on_einfo_code_button',
            'input .einfo_input': 'on_input_change',
            'click .einfo_code_generate': 'on_generate',
        }),
        /**
         * @override
         */
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            this._setValues();
            this.sequence_rule_lines = []
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @override
         * @returns {jQuery}
         */
        getFocusableElement: function () {
            return this.$el.is('select') ? this.$el : $();
        },
        /**
         * @override
         */
        isSet: function () {
            return this.value !== false;
        },
        /**
         * Listen to modifiers updates to hide/show the falsy value in the dropdown
         * according to the required modifier.
         *
         * @override
         */
        updateModifiersValue: function () {
            this._super.apply(this, arguments);
            if (!this.attrs.modifiersValue.invisible && this.mode !== 'readonly') {
                this._setValues();
                this._renderEdit();
            }
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _renderEdit: function () {
            this.einfo_render()
        },
        /**
         * @override
         * @private
         */
        _renderReadonly: function () {
            this.einfo_render()
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
        /**
         * @override
         */
        _reset: function () {
            this._super.apply(this, arguments);
            this._setValues();
        },
        /**
         * Sets the possible field values. If the field is a many2one, those values
         * may change during the lifecycle of the widget if the domain change (an
         * onchange may change the domain).
         *
         * @private
         */
        _setValues: function () {
            var self = this

            this.values = []
            this._rpc({
                model: 'einfo.code.rule',
                method: 'get_rule_data',
                args: [this.res_id],
            }).then(function (result) {
                self.values = result
                // console.log(result)
                self._render()
            })
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * The small slight difficulty is that we have to set the value differently
         * depending on the field type.
         *
         * @private
         */
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
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'einfo.code.rule.wizard',
                target: 'new',
                views: [[false, 'form']],
                context: { 'einfo_code_rule_id': this.res_id, 'name': code, 'sequence_rule_lines': this.sequence_rule_lines },
            });

            //
            // var self = this
            // var $content = $('<div><span>编号：</span><h2>' + code + '</h2><span>编号描述说明：</span><textarea id="einfo_code_desc" class="o_field_text o_field_widget o_input oe_inline" name="note" placeholder="" type="text" ></textarea></div>')
            // this.dialog = new Dialog(this, {
            //     title: _t('确认生成编号吗?'),
            //     buttons: [{
            //         text: _t('确认'), classes: 'btn-primary', close: false, click: function () {
            //             var description = $('#einfo_code_desc').val()
            //             this._rpc({
            //                 model: 'einfo.code.rule',
            //                 method: 'generate_code',
            //                 args: [self.res_id, code, description],
            //             }).then(function (result) {
            //                 console.log(result)
            //                 self.do_action({ effect: false, type: 'ir.actions.act_window_close' });
            //             })
            //         }
            //     }, { text: _t('取消'), close: true }],
            //     $content: $content,
            // });
            // this.dialog.open();
        }
    });
    registry.add('code_generate_array', CodeGenerateArray)
})    