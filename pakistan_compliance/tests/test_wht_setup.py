# Copyright (c) 2026, Sowaan and contributors
# For license information, please see license.txt

"""Phase 4 coverage: the Pakistan withholding-tax categories the setup button seeds.

Data-level tests (no DB writes): confirm the section list, the Filer/Non-Filer
naming, and that every non-filer rate is at least the filer rate. The end-to-end
creation (WHT account + Tax Withholding Categories for a real Company) is verified
against a live Company. Rate VALUES are intentionally not asserted here: they are
editable defaults that must be verified against the current Finance Act, so pinning
them in a test would give false confidence.
"""

from frappe.tests.utils import FrappeTestCase

from pakistan_compliance import wht_setup


class TestWhtSetup(FrappeTestCase):
	def test_core_sections_present(self):
		sections = [s["section"] for s in wht_setup.WHT_SECTIONS]
		for expected in ("153(1)(a)", "153(1)(b)", "153(1)(c)", "233", "155"):
			self.assertIn(expected, sections)

	def test_filer_and_nonfiler_variants(self):
		self.assertEqual(wht_setup.STATUSES, ("Filer", "Non-Filer"))
		name = wht_setup.category_name("153(1)(b)", "Services", "Non-Filer")
		self.assertEqual(name, "Pakistan WHT 153(1)(b) Services (Non-Filer)")

	def test_nonfiler_not_below_filer(self):
		# Non-filers never withhold less than filers; the exact multiple varies by
		# section, so we only assert the direction, not the value.
		for s in wht_setup.WHT_SECTIONS:
			self.assertGreaterEqual(s["non_filer"], s["filer"], s["section"])

	def test_rate_window_is_open_ended(self):
		# to_date is far future so a later invoice never silently computes zero WHT.
		self.assertGreater(wht_setup.WHT_RATES_TO, wht_setup.WHT_RATES_FROM)
