odoo.define('product.appoval', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var field_utils = require('web.field_utils');
    
    var QWeb = core.qweb;

    var SearchProductInfo = AbstractField.extend({
        events: _.extend({
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
        /**
         * @private
         * @override
         */
        _render: function() {
            var self = this;
            console.log("hhhahahahahahaha")
            console.log(self)
            // this.values = JSON.parse(this.value);
            // console.log(this.values)
            // if (!this.values) {
            //     this.$el.html('');
            //     return;
            // }
            // this.$el.html(QWeb.render('CodeGenerateWidget', {
            //     values: this.values,
            // }));

        },

    });

    core.form_widget_registry.add('search_product_info', SearchProductInfo);
})