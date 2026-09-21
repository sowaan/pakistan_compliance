# Copyright (c) 2026, Sowaan and contributors
# For license information, please see license.txt

"""Install / migrate setup for Pakistan Compliance (Phase 1).

Adds the Pakistan tax master-data fields to the standard doctypes. Idempotent:
create_custom_fields skips fields that already exist, so this is safe to run on
every install and every migrate.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

# Pakistan's tax jurisdictions (province + the two federal territories treated as
# such for sales tax on services). Leading blank so the field is optional.
PROVINCES = (
	"\nPunjab\nSindh\nKhyber Pakhtunkhwa\nBalochistan\n"
	"Islamabad Capital Territory\nGilgit-Baltistan\nAzad Jammu and Kashmir"
)

# Filer status drives withholding-tax rates (non-filers pay more). Leading blank.
FILER_STATUS = "\nFiler\nNon-Filer"


def _tax_identity_fields(insert_after):
	"""NTN + STRN pair, shared by Company / Customer / Supplier.

	These are plain fields (no Section/Column Break). Frappe's meta places a custom
	Section Break just before the NEXT existing section break, which on Customer has
	none inside the Tax tab and so pushes it into a later tab. Plain Data/Select
	fields are placed exactly after their `insert_after`, so they stay in the Tax
	tab's tax section."""
	return [
		{
			"fieldname": "custom_ntn",
			"fieldtype": "Data",
			"label": "NTN (National Tax Number)",
			"insert_after": insert_after,
			"translatable": 0,
		},
		{
			"fieldname": "custom_strn",
			"fieldtype": "Data",
			"label": "STRN (Sales Tax Registration Number)",
			"insert_after": "custom_ntn",
			"translatable": 0,
		},
	]


def _party_extra_fields():
	"""CNIC + filer status on Customer / Supplier, laid out as a second column so
	the four Pakistan fields read as NTN/STRN | CNIC/Filer. The Column Break is
	anchored to a custom field (custom_strn), so Frappe places it exactly there;
	the section/column skip-ahead only triggers when the anchor is a standard
	field already in the field order."""
	return [
		{
			"fieldname": "custom_pk_tax_column_break",
			"fieldtype": "Column Break",
			"insert_after": "custom_strn",
		},
		{
			"fieldname": "custom_cnic",
			"fieldtype": "Data",
			"label": "CNIC",
			"insert_after": "custom_pk_tax_column_break",
			"translatable": 0,
			"description": "13-digit national ID, required on invoices to unregistered buyers above the FBR threshold.",
		},
		{
			"fieldname": "custom_filer_status",
			"fieldtype": "Select",
			"label": "Filer Status (ATL)",
			"options": FILER_STATUS,
			"insert_after": "custom_cnic",
			"description": "Active Taxpayer List status. Affects withholding-tax rates.",
		},
	]


CUSTOM_FIELDS = {
	# Company has no Tax tab; its tax_id sits in the top "details" section, so anchor
	# there. Customer/Supplier have a Tax tab whose last field is
	# tax_withholding_category, so anchor to it to keep the Pakistan Tax section
	# inside the Tax tab (anchoring to tax_id, mid-section, pushed it to a later tab).
	"Company": _tax_identity_fields("tax_id"),
	"Customer": _tax_identity_fields("tax_withholding_category") + _party_extra_fields(),
	"Supplier": _tax_identity_fields("tax_withholding_category") + _party_extra_fields(),
	"Item": [
		{
			"fieldname": "custom_hs_code",
			"fieldtype": "Data",
			"label": "HS Code",
			"insert_after": "item_group",
			"translatable": 0,
			"description": "Harmonized System code, required on FBR sales tax invoices.",
		}
	],
	"Address": [
		{
			"fieldname": "custom_province",
			"fieldtype": "Select",
			"label": "Province",
			"options": PROVINCES,
			"insert_after": "state",
			"description": "Determines the sales-tax-on-services authority (SRB / PRA / KPRA / BRA / ICT).",
		}
	],
}


def ensure_custom_fields():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)


def after_install():
	ensure_custom_fields()


def after_migrate():
	ensure_custom_fields()
