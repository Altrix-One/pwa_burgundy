// Copyright (c) 2024, Aerele Technologies Private Limited and contributors
// For license information, please see license.txt

// frappe.ui.form.on("PWA Form", {
// 	refresh(frm) {
frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        // Initialize the BarcodeScanner
        const scanner = new erpnext.utils.BarcodeScanner({
            on_scan: function(barcode) {
                // Call the function to add or update the item in the "Items" table
                add_or_update_item(frm, barcode);
            }
        });

        // Start barcode scanning when the user focuses on the barcode field
        frm.fields_dict.scan_barcode.$input.on('focus', function() {
            scanner.start();
        });

        // Stop scanning when the barcode field loses focus
        frm.fields_dict.scan_barcode.$input.on('blur', function() {
            scanner.stop();
        });
    }
});

// Function to add or update an item in the "Items" table
function add_or_update_item(frm, barcode) {
    frappe.call({
        method: "erpnext.stock.get_item_details.get_item_by_barcode",
        args: {
            barcode: barcode
        },
        callback: function(response) {
            if (response.message) {
                let item_code = response.message.item_code;
                let existing_row = frm.doc.items.find(row => row.item_code === item_code);

                if (existing_row) {
                    // Item already exists, increase the quantity
                    frappe.model.set_value(existing_row.doctype, existing_row.name, 'qty', existing_row.qty + 1);
                    frappe.show_alert({message: `Updated quantity for item: ${item_code}`, indicator: 'green'});
                } else {
                    // Item doesn't exist, add a new row
                    let new_row = frm.add_child('items');
                    frappe.model.set_value(new_row.doctype, new_row.name, 'item_code', item_code);
                    frappe.model.set_value(new_row.doctype, new_row.name, 'qty', 1);
                    frappe.model.set_value(new_row.doctype, new_row.name, 'barcode', barcode);
                    frm.refresh_field('items');
                    frappe.show_alert({message: `Added new item: ${item_code}`, indicator: 'green'});
                }
            } else {
                frappe.msgprint(__('Item not found for barcode {0}', [barcode]));
            }
        }
    });
}

// 	},
// });
