import frappe

@frappe.whitelist()
def get_form_meta(form, doctype):
	meta_data={}
	if doc := frappe.get_doc("PWA Form", {"form_name": form, "doctype_name": doctype}):
		fields = []
		for field in doc.pwa_form_fields:
			row = {
				"idx" : field.idx,
				"label" : field.label,
				"fieldname" : field.fieldname,
				"fieldtype" : field.fieldtype,
				"reqd" : field.reqd,
				"default" : field.default,
				"read_only" : field.read_only,
				"description" : field.description,
				"options" : field.options
			}
			if field.fieldtype == "Select":
				row['options'] = [{'label': option, 'value': option} for option in field.options.split('\n')]

			fields.append(row)

		meta_data = {
			"form_name" : doc.form_name,
			"doctype_name" : doc.doctype_name,
			"parent_form" : doc.parent_form,
			"is_submittable" : doc.is_submittable,
			"is_child_table" : doc.is_child_table,
			"fields" : fields,
		}
	return meta_data
