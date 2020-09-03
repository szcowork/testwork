odoo.define('einfo_code_manager.code_generate_widget', function (require) {
    "use strict";
    
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var field_utils = require('web.field_utils');
    
    var QWeb = core.qweb;
    
    
    var code_generate_widget = AbstractField.extend({
        events: _.extend({
            // 'click .e_radio_item': '_on_radio_item',
        }, AbstractField.prototype.events),
        supportedFieldTypes: ['char'],
    
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
    
        /**
         * @override
         * @returns {boolean}
         */
        isSet: function() {
            return true;
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * @private
         * @override
         */
        _render: function() {
            var self = this;
            this.values = JSON.parse(this.value);
            console.log(this.values)
            if (!this.values) {
                this.$el.html('');
                return;
            }
            this.$el.html(QWeb.render('CodeGenerateWidget', {
                values: this.values,
            }));
            // _.each(info.content, function (k, v){
            //     k.index = v;
            //     k.amount = field_utils.format.float(k.amount, {digits: k.digits});
            //     if (k.date){
            //         k.date = field_utils.format.date(field_utils.parse.date(k.date, {}, {isUTC: true}));
            //     }
            // });
            // this.$el.html(QWeb.render('ShowPaymentInfo', {
            //     lines: info.content,
            //     outstanding: info.outstanding,
            //     title: info.title
            // }));

        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        _on_radio_item:function(event){
            var i = $(event.target).data('i');
            var j = $(event.target).data('j');
            this.values[i].checked = j
            this._render()
        },

        // /**
        //  * @private
        //  * @override
        //  * @param {MouseEvent} event
        //  */
        // _onRemoveMoveReconcile: function (event) {
        //     var self = this;
        //     var paymentId = parseInt($(event.target).attr('payment-id'));
        //     if (paymentId !== undefined && !isNaN(paymentId)){
        //         this._rpc({
        //             model: 'account.move.line',
        //             method: 'remove_move_reconcile',
        //             args: [paymentId, {'invoice_id': this.res_id}]
        //         }).then(function () {
        //             self.trigger_up('reload');
        //         });
        //     }
        // },
    });
    
    field_registry.add('code_generate_widget', code_generate_widget);
    
    return {
        code_generate_widget: code_generate_widget
    };
        
    });
    