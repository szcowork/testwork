odoo.define('product.appoval', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var field_utils = require('web.field_utils');
    
    var QWeb = core.qweb;

    var search_product_info = AbstractField.extend({
        /**
         * @override
         */
        init: function() {
            this._super.apply(this, arguments);

            console.log("hhhahahahahahaha")
            console.log(this)
        },

    });

    // core.form_widget_registry.add('search_product_info', search_product_info);
    field_registry.add('search_product_info', search_product_info);
    
    return {
        search_product_info: search_product_info
    };
})