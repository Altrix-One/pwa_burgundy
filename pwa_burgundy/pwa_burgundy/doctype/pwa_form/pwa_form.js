// Copyright (c) 2024, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

// frappe.ui.form.on("PWA Form", {
// 	refresh(frm) {
frappe.ui.form.on('PWA Form', {
    refresh: function(frm) {
        // Initialize the BarcodeScanner
        const scanner = new erpnext.utils.BarcodeScanner({
            on_scan: function(barcode) {
                // Automatically populate the barcode field with the scanned value
                frm.set_value('scan_barcode', barcode);
                frappe.show_alert({message: `Barcode scanned: ${barcode}`, indicator: 'green'});
            }
        });

        // Trigger the barcode scanner when user selects the barcode field
        frm.fields_dict.scan_barcode.$input.on('focus', function() {
            scanner.start();
        });
        
        // Stop scanning when field is out of focus
        frm.fields_dict.scan_barcode.$input.on('blur', function() {
            scanner.stop();
        });
    }
});

// 	},
// });
