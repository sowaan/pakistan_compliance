# Copyright (c) 2026, Sowaan and contributors
# For license information, please see license.txt

"""Shared helpers for Pakistan Compliance.

`money_in_words_urdu` spells a money amount in Urdu, mirroring the KSA app's
Arabic amount-in-words but backed by `indic-numtowords` because `num2words` has
no Urdu (or Hindi) backend. It is exposed to Jinja (see the `jinja` hook in
hooks.py) so print formats can render it at print time without any stored field:

    {{ money_in_words_urdu(doc.grand_total, doc.currency) }}
"""

import frappe
from frappe.utils import flt

# Urdu name of each supported currency: (main unit, 1/100 sub-unit).
# Unknown currencies fall back to the ISO code itself so we never mislabel one.
CURRENCY_UR = {
	"PKR": ("روپے", "پیسے"),
	"USD": ("امریکی ڈالر", "سینٹ"),
	"EUR": ("یورو", "سینٹ"),
	"GBP": ("برطانوی پاؤنڈ", "پینس"),
	"SAR": ("سعودی ریال", "ہلالہ"),
	"AED": ("اماراتی درہم", "فلس"),
	"INR": ("بھارتی روپے", "پیسے"),
}


def _num2words_urdu(number):
	"""Integer -> Urdu words via indic-numtowords (South Asian lakh/crore grouping)."""
	from indic_numtowords import num2words

	return num2words(int(number), lang="ur")


def money_in_words_urdu(amount, currency=None):
	"""Return `amount` spelled out in Urdu, e.g. 'ستر ہزار ایک سو اسی روپے فقط'.

	Handles the paisa (sub-unit) part and negative totals (credit / debit notes
	carry a negative grand_total). Returns '' on any failure so a print format
	never breaks over an amount it cannot spell."""
	try:
		amount = abs(flt(amount))
		main = int(amount)
		fraction = int(round((amount - main) * 100))
		if fraction == 100:  # rounding pushed it to the next whole unit
			main += 1
			fraction = 0

		main_name, fraction_name = CURRENCY_UR.get(
			(currency or "PKR").upper(), (currency or "PKR", None)
		)

		words = f"{_num2words_urdu(main)} {main_name}"
		if fraction and fraction_name:
			words += f" اور {_num2words_urdu(fraction)} {fraction_name}"
		return f"{words} فقط"
	except Exception:
		frappe.log_error(title="Pakistan Compliance: Urdu in-words failed")
		return ""
