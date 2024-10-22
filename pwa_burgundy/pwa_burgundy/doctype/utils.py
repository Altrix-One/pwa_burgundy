import json

import frappe
import frappe
from frappe import _
from frappe.query_builder.functions import CombineDatetime, IfNull, Sum
from frappe.utils import cstr, flt, get_link_to_form, get_time, getdate, nowdate, nowtime

@frappe.whitelist()
def get_stock_balance(
	item_code,
	warehouse,
	posting_date=None,
	posting_time=None,
	with_valuation_rate=False,
	with_serial_no=False,
	inventory_dimensions_dict=None,
):
	"""Returns stock balance quantity at given warehouse on given posting date or current date.

	If `with_valuation_rate` is True, will return tuple (qty, rate)"""

	from erpnext.stock.stock_ledger import get_previous_sle

	if posting_date is None:
		posting_date = nowdate()
	if posting_time is None:
		posting_time = nowtime()

	args = {
		"item_code": item_code,
		"warehouse": warehouse,
		"posting_date": posting_date,
		"posting_time": posting_time,
	}

	extra_cond = ""
	if inventory_dimensions_dict:
		for field, value in inventory_dimensions_dict.items():
			args[field] = value
			extra_cond += f" and {field} = %({field})s"

	last_entry = get_previous_sle(args, extra_cond=extra_cond)

	if with_valuation_rate:
		if with_serial_no:
			serial_no_details = get_available_serial_nos(
				frappe._dict(
					{
						"item_code": item_code,
						"warehouse": warehouse,
						"posting_date": posting_date,
						"posting_time": posting_time,
						"ignore_warehouse": 1,
					}
				)
			)

			serial_nos = ""
			if serial_no_details:
				serial_nos = "\n".join(d.serial_no for d in serial_no_details)

			return (
				(last_entry.qty_after_transaction, last_entry.valuation_rate, serial_nos)
				if last_entry
				else (0.0, 0.0, None)
			)
		else:
			return (last_entry.qty_after_transaction, last_entry.valuation_rate) if last_entry else (0.0, 0.0)
	else:
		return last_entry.qty_after_transaction if last_entry else 0.0
	
@frappe.whitelist()
def scan_barcode(search_value: str) -> BarcodeScanResult:
	def set_cache(data: BarcodeScanResult):
		frappe.cache().set_value(f"erpnext:barcode_scan:{search_value}", data, expires_in_sec=120)

	def get_cache() -> BarcodeScanResult | None:
		if data := frappe.cache().get_value(f"erpnext:barcode_scan:{search_value}"):
			return data

	if scan_data := get_cache():
		return scan_data

	# search barcode no
	barcode_data = frappe.db.get_value(
		"Item Barcode",
		{"barcode": search_value},
		["barcode", "parent as item_code", "uom"],
		as_dict=True,
	)
	if barcode_data:
		_update_item_info(barcode_data)
		set_cache(barcode_data)
		return barcode_data

	# search serial no
	serial_no_data = frappe.db.get_value(
		"Serial No",
		search_value,
		["name as serial_no", "item_code", "batch_no"],
		as_dict=True,
	)
	if serial_no_data:
		_update_item_info(serial_no_data)
		set_cache(serial_no_data)
		return serial_no_data

	# search batch no
	batch_no_data = frappe.db.get_value(
		"Batch",
		search_value,
		["name as batch_no", "item as item_code"],
		as_dict=True,
	)
	if batch_no_data:
		if frappe.get_cached_value("Item", batch_no_data.item_code, "has_serial_no"):
			frappe.throw(
				_(
					"Batch No {0} is linked with Item {1} which has serial no. Please scan serial no instead."
				).format(search_value, batch_no_data.item_code)
			)

		_update_item_info(batch_no_data)
		set_cache(batch_no_data)
		return batch_no_data

	return {}

def get_stock_value_on(
	warehouses: list | str | None = None, posting_date: str | None = None, item_code: str | None = None
) -> float:
	if not posting_date:
		posting_date = nowdate()

	sle = frappe.qb.DocType("Stock Ledger Entry")
	query = (
		frappe.qb.from_(sle)
		.select(IfNull(Sum(sle.stock_value_difference), 0))
		.where((sle.posting_date <= posting_date) & (sle.is_cancelled == 0))
	)

	if warehouses:
		if isinstance(warehouses, str):
			warehouses = [warehouses]

		warehouses = set(warehouses)
		for wh in list(warehouses):
			if frappe.db.get_value("Warehouse", wh, "is_group"):
				warehouses.update(get_child_warehouses(wh))

		query = query.where(sle.warehouse.isin(warehouses))

	if item_code:
		query = query.where(sle.item_code == item_code)

	return query.run(as_list=True)[0][0]
