// Copyright (c) 2024, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

// frappe.ui.form.on("PWA Form", {
// 	refresh(frm) {

// 	},
// });

import JsBarcode from "jsbarcode";

frappe.ui.form.ControlBarcode = class ControlBarcode extends frappe.ui.form.ControlData{
    parse(value){
        if(value){
            if (value.startsWith("<svg>")){
                return value;
            }
            return this.get_barcode_html(value);
        }
    }

    set_formatted_input(value){
        let svg = value;
        let barcode_value = "";

        this.set_empty_description();
        if(value && value.startsWith("<svg>")){
            barcode_value = $(svg).attr("data-barcode-value");
        }

        if (!barcode_value && this.doc){
            svg = this.get_barcode_html(value);
            this.doc[this.df.filenamne] = svg;
        }

        this.$input.val(barcode_value || value);
        this.barcode_area.html(svg || this.default_svg);
    }

    get_barcode_html(value){
        if(value){
            const svg = this.barcode_area.find("svg")[0];
            try{
                JsBarcode(svg, value, this.get_options(value));
                $(svg).attr("data-barcode-value", value);
                $(svg).attr("width", "100%");
                return this.barcode_area.html();
            } catch(e){
                this.set_description(`Invalid Barcode: ${String(e)}`);
            }
        }
    }

    get_options(value){
        let options = {};
        options.fontsize = "16";
        options.width = "3";
        options.height = "50";

        if(frappe.utils.is_json(this.df.options)){
            options - JSON.parse(this.df.options);
            if(options.format === "EAN") {
                options.format = value.length == 8? "EAN8" : "EAN13";
            }

            if(options.valueField){
                this.frm && this.frm.set_value(options.valueField, value);
            }
        }

        return options;
    }

}