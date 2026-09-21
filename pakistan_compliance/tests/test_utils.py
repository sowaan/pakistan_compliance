# Copyright (c) 2026, Sowaan and contributors
# For license information, please see license.txt

"""Offline tests for the Urdu amount-in-words helper (Phase 3)."""

import unittest

from pakistan_compliance.utils import money_in_words_urdu


class TestUrduInWords(unittest.TestCase):
	def test_whole_rupees(self):
		# 70180 -> seventy thousand one hundred eighty rupees only
		self.assertEqual(money_in_words_urdu(70180, "PKR"), "ستر ہزار ایک سو اسی روپے فقط")

	def test_lakh_crore_grouping(self):
		# South Asian grouping: 100000 is one lakh, not "hundred thousand"
		self.assertEqual(money_in_words_urdu(100000, "PKR"), "ایک لاکھ روپے فقط")
		self.assertIn("کروڑ", money_in_words_urdu(10000000, "PKR"))

	def test_paisa_subunit(self):
		words = money_in_words_urdu(1740.50, "PKR")
		self.assertIn("اور", words)  # joins rupees "and" paisa
		self.assertIn("پیسے", words)
		self.assertTrue(words.endswith("فقط"))

	def test_negative_is_absolute(self):
		# Credit / debit notes carry a negative grand_total; magnitude is spelled.
		self.assertEqual(money_in_words_urdu(-70180, "PKR"), money_in_words_urdu(70180, "PKR"))

	def test_zero(self):
		self.assertEqual(money_in_words_urdu(0, "PKR"), "صفر روپے فقط")

	def test_non_pkr_currency_named(self):
		words = money_in_words_urdu(100.25, "USD")
		self.assertIn("ڈالر", words)  # US dollar main unit
		self.assertIn("سینٹ", words)  # cent sub-unit

	def test_unknown_currency_falls_back_to_code(self):
		# Never mislabel: an unmapped code is used verbatim as the unit name.
		words = money_in_words_urdu(5, "XYZ")
		self.assertIn("XYZ", words)

	def test_rounding_to_next_whole_unit(self):
		# 9.999 rounds the paisa up to 100 -> carries into the whole unit, no "100 paise".
		words = money_in_words_urdu(9.999, "PKR")
		self.assertNotIn("پیسے", words)
		self.assertEqual(words, money_in_words_urdu(10, "PKR"))


if __name__ == "__main__":
	unittest.main()
