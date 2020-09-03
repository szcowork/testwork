odoo.define('einfo.code_manager', function (require) {
    "use strict";
    var registry = require('web.field_registry');
    var basic_fields = require('web.basic_fields');
    var kw_FieldText = basic_fields.FieldText.extend({
        /**
         * @override
         */
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            console.log(this) 
        },
    });
    registry.add('kw_field_text', kw_FieldText)
})    