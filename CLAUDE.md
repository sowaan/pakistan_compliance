# CLAUDE.md, Pakistan Compliance (ERPNext localization for Pakistan)

This file is the standing brief for any developer or AI coding agent working in this repository.
Read it before writing code. It defines what we are building, the guardrails that apply at every
phase, and a phase-by-phase build plan. Treat the phase list as the backlog: do not jump ahead to a
later phase before the current phase's acceptance criteria are met, and update the "Current Phase"
marker below when a phase is completed.

**Current Phase:** 3, Print formats (done bar one). Shipped, all sharing one green (#0b6e4f) design
system: **FBR Sales Tax Invoice**, **FBR Sales Tax Credit Note**, **Pakistan Sales Order**,
**Pakistan Delivery Challan**, **Pakistan Purchase Order**, **Pakistan Quotation**, **Pakistan
Payment Voucher** (dynamic Receipt/Payment), plus the **Urdu amount-in-words** helper and its toggle.
Each is set as its DocType's default on install (`ensure_default_print_formats(force=True)` in
after_install overrides the ERPNext framework default e.g. 'Sales Order with Item Image'); on
migrate it is force=False so a customer's own default is never overridden. The Credit Note shares
the Sales Invoice DocType with the invoice (which owns that default), so it stays manually
selectable. The **Withholding Tax Certificate** is the only Phase 3 item left and waits for Phase
4's WHT logic.

**Phase 4 (withholding tax + ATL) started.** Approach: reuse ERPNext's native **Tax Withholding
Category** rather than build a parallel engine. `wht_setup.py` has a whitelisted
`setup_company_wht(company)` (button on Pakistan Tax Settings) that creates a WHT payable account
under the company's Duties and Taxes group and one Tax Withholding Category per income-tax section
in Filer and Non-Filer variants (153(1)(a) goods, 153(1)(b) services, 153(1)(c) contracts, 233
commission, 155 rent). Idempotent; verified live on a real Company (account + 10 categories). Only
common v15/v16 fields are set on the category (category_name, rates, accounts, round_off_tax_amount).

**Phase 4 is code-complete; live sign-off on rates still pending.**

Rates: `WHT_SECTIONS` now carries the FBR **tax year 2026** (Finance Act 2025) rates from the
official FBR Withholding Income Tax Rate Card, cross-checked against KPMG/TAG/PwC/Grant Thornton
(153(1)(a) goods 5/10, 153(1)(b) services 15/30 general, 153(1)(c) contracts 7.5/15, 233 commission
12/24, 155 rent 15/30 company). Company rate used where a company/non-company split exists; reduced
service carve-outs (6/12, 4/8, 1.5/3) and the individual/AOP slab for 155 are documented in
`wht_setup.py` comments. Re-verify each Finance Act; a user still confirms before production.

v16 support: DONE. v15 applies WHT as a "Deduct" tax row at validation; v16 reworked it to be
item-driven (`item.tax_withholding_category` + `item.apply_tds` -> a `Tax Withholding Entry` on
submit). `wht_setup.propagate_item_wht` (validate hook on Purchase Invoice/Order) copies the
supplier's WHT category down to item rows so supplier-level config deducts on both versions. Verified
live on v16: Filer PI deducts 10%, Non-Filer 20%, each posting a Tax Withholding Entry + GL credit to
Withholding Tax Payable.

WHT Certificate: DONE. A submittable **Withholding Tax Certificate** DocType (company, supplier,
period, deductions, totals) with a "Fetch Deductions" button that reads GL entries against the
company's WHT accounts (cross-version; the WHT GL line has no party, so each voucher is matched to
its own supplier), plus a green **Pakistan Withholding Tax Certificate** print format (English + Urdu
total-in-words, Income Tax Ordinance 2001 certification). Set as the doctype default.

Remaining before "done": the live acceptance ("a payment/purchase correctly computes and posts WHT
for a filer and a non-filer") is proven on v16 in a console session; a real submitted-and-committed
document on the site plus final rate sign-off close the phase. Suppliers are assigned the matching
(Filer)/(Non-Filer) category manually; an auto-assign-by-filer-status helper is a possible follow-up.

Print-format build notes (for the next agent): each format is a standard Jinja Print Format shipped
as an app file under `print_format/<scrubbed>/`. The print Jinja sandbox exposes only a subset of
`frappe` (use `frappe.db.get_value`, NOT `frappe.get_cached_value`), plus our own `jinja` methods
(`money_in_words_urdu`, `show_urdu_in_words`, `fmt_money_abs`) and `frappe.utils.money_in_words` for
English. Returns/credit notes carry negative amounts, so the credit note uses `fmt_money_abs` and
`| abs` to print magnitudes. After editing a shipped format's JSON you MUST bump its `modified`
timestamp or `reload-doc` skips the update.

Phase 3 so far: a standard **"FBR Sales Tax Invoice"** print format (Jinja, shipped as an app
file under `print_format/fbr_sales_tax_invoice/`) for Sales Invoice: seller and buyer NTN/STRN
(CNIC fallback for unregistered buyers), per-line HS Code (from Item `custom_hs_code`), value
excluding tax, the full tax breakdown from `doc.taxes` (Sales Tax 18%, Further Tax 3%, provincial,
etc.), grand total, and amount in words. `install.py` now also sets it as the default print format
for Sales Invoice via a durable Property Setter (`ensure_default_print_formats`, idempotent).
Render-verified with sample data.

**Urdu amount-in-words** now done (was deferred): `num2words` has no Urdu backend, so we use
`indic-numtowords` (MIT, no deps) via `utils.money_in_words_urdu(amount, currency)`, exposed to
Jinja through the `jinja` hook so print formats call it at render time (no stored field). Handles
paisa sub-units, negative totals (credit/debit notes), rounding carry, and per-currency unit names
(PKR roupe/paisa, plus USD/EUR/GBP/SAR/AED/INR; unknown codes used verbatim, never mislabeled). The
FBR Sales Tax Invoice renders it RTL under the English line, gated by a **"Show Urdu Amount in
Words"** toggle (a Print Formats section on Pakistan Tax Settings, on by default). Because a Single's
field default only applies once saved and an unset Check reads back as 0, install.py seeds the
default to on when it has never been set, while leaving a customer's explicit off alone. 11 offline
tests (test_utils.py).

Phase 2 shipped: a **"Set up Pakistan Taxes"** button on Pakistan Tax Settings (prompts for a
Company) that runs `tax_setup.setup_company_taxes` to idempotently create, under the company's
Duties and Taxes group: output/input tax accounts (Sales Tax Payable, Further Tax Payable, Input
Sales Tax, and per-province payables) and the Sales/Purchase Taxes and Charges Templates (federal
18%, 18% + further 3%, provincial services SRB 13% / PRA 16% / KPRA 15% / BRA 15% / ICT 15%, zero
rated, exempt, plus input equivalents). Rates are the confirmed current defaults; re-running skips
what exists. Workspace grew a Taxes card (tax templates, item tax template, chart of accounts). The
customer-facing field placement fix from Phase 1 also landed here (Pakistan Tax section in the Tax
tab, 2 columns, via a field_order property setter). 9 offline tests. Verified end-to-end on a real
Company (accounts + all templates created).

Phase 1 shipped: **Pakistan Tax Settings** single DocType (enabled, default_province, FBR section
with environment + base URL + encrypted token, hidden default_data_seeded flag for Phase 2), and the
master-data custom fields created idempotently via `install.py` on after_install/after_migrate:
NTN + STRN on Company/Customer/Supplier, CNIC + Filer Status (ATL) on Customer/Supplier, HS Code on
Item, Province on Address. 4 offline tests. Verified on v16 (migrate creates the doctype + all
fields).

## 1. What this app is

**App name: `pakistan_compliance`** (Frappe module: "Pakistan Compliance"). A single Frappe/ERPNext
app that makes a Pakistani business tax-compliant and locally presentable inside ERPNext: FBR sales
tax invoices and other print formats, the tax setup (federal and provincial sales tax, further tax,
withholding tax) with its Chart of Accounts, withholding-tax handling with filer/non-filer (ATL)
awareness, and integration with FBR's Digital Invoicing system (real-time e-invoicing that returns
an Invoice Reference Number and QR code).

It is the Pakistan counterpart to the KSA work in the sibling repos (`ksa_print_formats` for the
print formats and `zatca` for the e-invoicing integration). Here it is deliberately kept as **one
app**, not two. If the FBR e-invoicing piece grows heavy it can be split later, but start unified.

**Compatibility:** ERPNext / Frappe **v15** (branch `main`) and **v16** (branch `version-16`). Keep
the code working on both. Avoid v16-only framework APIs, or guard them by version. The only expected
per-branch difference is `[tool.bench.frappe-dependencies]` in `pyproject.toml`.

## 2. Non-negotiable guardrails (read before writing any code)

1. **Never hardcode tax rates or rules as permanent truth.** Pakistani rates and rules change every
   year (Finance Acts) and often mid-year (SROs). Rates live in configurable Tax Templates / Settings,
   never buried in code. Any seeded default must carry a comment with its source and date and must be
   trivial to change. When unsure of a current rate or rule, flag it and ask; do not guess.
2. **FBR is the source of truth for e-invoicing, not our assumptions.** Integrate against the FBR /
   PRAL Digital Invoicing API and its sandbox the same way the `zatca` app treats the ZATCA API:
   trust the live sandbox over any document, test against it, and flag contract mismatches upstream
   rather than silently coding around them.
3. **Credentials are sensitive.** FBR/PRAL tokens and any API keys are stored with Frappe's encrypted
   `Password` fieldtype, never in plain `Data`, never logged (scrub them from any exception handler),
   and never echoed back to the browser beyond confirming they are set.
4. **Do not fabricate compliance.** If a legal detail is uncertain (a CNIC threshold, a WHT section
   rate, whether further tax applies), surface it for confirmation against current law rather than
   inventing a value. Being wrong about tax is worse than asking.
5. **Setup must be idempotent and must respect the customer's edits.** Creating tax templates, CoA
   accounts, custom fields, and default print formats must be safe to run on every install/migrate
   and must not overwrite values a customer has changed. Use a "seeded" flag and skip-if-exists.
6. **Keep federal and provincial tax separate.** Sales tax on goods is federal (FBR); sales tax on
   services is provincial (SRB/PRA/KPRA/BRA) and ICT. Do not conflate them; model province on Address
   and pick the right authority/rate accordingly.
7. **No em dash character (`-` U+2014) in user-facing text or code comments.** Use plain punctuation.

## 3. Tech stack (locked)

| Layer | Choice | Why |
|---|---|---|
| Framework | Frappe (Python), v15 and v16 | This is a Frappe app. |
| Language | Python 3.10+ | Frappe's minimum; keeps v15 working. |
| Data model | Frappe DocTypes | Settings, FBR logs, WHT config, etc. Standard patterns. |
| HTTP client | plain `requests` | FBR/PRAL REST API. A thin wrapper module (`fbr_client.py`), no heavy SDK. |
| Templating | Frappe Jinja (`frappe.render_template`) | Same engine Print Formats use. No second engine. |
| Amount in words | `indic-numtowords` (Urdu) | `num2words` has no Urdu/Hindi backend (verified 0.5.14, both raise NotImplementedError). `indic-numtowords` (MIT, no deps, py>=3.6) spells Urdu with correct South Asian lakh/crore grouping. Exposed to Jinja via `money_in_words_urdu` (see `utils.py` + the `jinja` hook). |
| Frontend | Frappe Desk (client scripts, standard views) | Native feel, no separate SPA. |
| Distribution | Standard installable Frappe app | Marketplace later (Phase 7). |

Do not add a second HTTP client, a second templating engine, or a separate service without updating
this table and getting sign-off.

## 4. Repository structure (target shape)

Single app. Package-level modules keep import/endpoint paths short; DocTypes stay under the module
dir (Frappe requires it).

```
pakistan_compliance/                     # repo root
  pakistan_compliance/                   # Python package (import root)
    __init__.py
    hooks.py
    modules.txt                          # -> "Pakistan Compliance"
    patches.txt
    install.py            / setup.py     # after_install / after_migrate: seed tax + fields + defaults
    default_data.py                      # tax templates, CoA, custom field defs (idempotent)
    utils.py                             # Urdu amount-in-words, helpers
    api/                                 # whitelisted methods (fbr submit, atl lookup, test connection)
      __init__.py
    fbr_client.py                        # thin FBR/PRAL Digital Invoicing REST wrapper (Phase 5)
    pakistan_compliance/                 # Frappe module dir (module "Pakistan Compliance")
      __init__.py
      doctype/
        pakistan_tax_settings/           # Single DocType: NTN/STRN, FBR creds, environment (Phase 1)
        fbr_invoice_log/                 # per-invoice FBR submission + IRN/QR (Phase 5)
        ...
      print_format/                      # FBR Sales Tax Invoice, Credit Note, Delivery Challan, ...
    public/
    config/
  README.md
  CLAUDE.md
  license.txt
  pyproject.toml
```

## 5. Development phases

### Phase 0, Scaffolding (DONE)
Installable app on the v16 bench, `main` (v15) and `version-16` (v16) branches, MIT license,
`[tool.bench.frappe-dependencies]` set per branch, `requires-python >=3.10`.
**Acceptance:** `bench install-app pakistan_compliance` succeeds on a real site.

### Phase 1, Settings and master data
- **Pakistan Tax Settings** (Single DocType): Company NTN, STRN, default province, FBR environment
  (sandbox/production), FBR/PRAL credentials (Password), toggles.
- **Custom fields:** NTN + STRN on Company/Customer/Supplier; CNIC on Customer/Supplier; HS Code on
  Item; Filer/Non-Filer (ATL) status on Customer/Supplier; Province on Address.
- A setup wizard/button skeleton (fill Company tax identity).
- **Acceptance:** an admin can set the company's tax identity and the custom fields appear on the
  standard forms.

### Phase 2, Tax setup automation
- Auto-create (idempotent) Sales Taxes and Charges Templates and their CoA accounts:
  federal sales tax on goods (standard rate, verify current), provincial sales tax on services per
  authority, further tax (3%), zero-rated, exempt.
- Item Tax Templates where relevant.
- **Acceptance:** after setup, a real invoice can apply the correct sales tax and it posts to the
  right accounts, verified live.

### Phase 3, Print formats
- FBR-compliant **Sales Tax Invoice** first (seller NTN/STRN, buyer NTN/STRN or CNIC, HS codes,
  value excl. tax, sales tax, further tax, WHT, totals), then Credit/Debit Note, Delivery Challan,
  Purchase Order, Quotation, Payment Voucher, Withholding Tax Certificate.
- **Urdu amount-in-words** field (mirrors the KSA Arabic approach; `num2words` Urdu).
- **Acceptance:** a real invoice renders a correct, professional FBR sales tax invoice, verified live.

### Phase 4, Withholding tax and ATL
- WHT deduction on purchases/payments by income-tax section, with filer/non-filer rate handling.
- Optional ATL (Active Taxpayer List) lookup for filer status.
- Withholding Tax Certificate generation.
- **Acceptance:** a payment/purchase correctly computes and posts WHT for a filer and a non-filer.

### Phase 5, FBR Digital Invoicing integration
- `fbr_client.py`: thin wrapper for the FBR/PRAL Digital Invoicing API (submit invoice, fetch status).
- Setup wizard: NTN/STRN, integrator token, environment (sandbox/production).
- On submit, post the invoice, receive the Invoice Reference Number (IRN) and QR, store them, and
  print them on the invoice. Handle B2B (registered) vs B2C.
- **Acceptance:** a real invoice is accepted by the FBR sandbox and prints a valid IRN + QR, verified
  live (the same way the `zatca` app verified against a real running stack).

### Phase 6, Reports
- Sales Tax Return annexures (Annexure-C sales, Annexure-A purchases) as exportable data.
- Withholding statements (e.g. the quarterly statement under section 165).
- **Acceptance:** the annexures reconcile with the posted invoices for a period.

### Phase 7, Marketplace packaging
- Screenshots, listing description (disclosure-first if any), Terms/Privacy, `main`+`version-16`
  branch mapping, licensing/pricing decision.
- **Acceptance:** installs cleanly on both supported ERPNext versions; listing content exists.

## 6. Notes for AI coding agents

- Do not skip ahead. Phase 2's tax setup must actually post correctly before Phase 3's invoice print
  is worth building on, and Phase 5's FBR integration must clear the sandbox before it is "done".
- `../ksa_print_formats` and `../zatca` (sibling apps in the KSA work) are good references for the
  print-format design system, the idempotent setup pattern, the amount-in-words utility (swap Arabic
  for Urdu), the encrypted-credential handling, and the setup wizard. Read them for conventions.
- Verify every tax rate, threshold, and API shape against the current official source at build time
  (FBR, the relevant provincial authority, or the FBR/PRAL sandbox). Flag anything uncertain.
- Keep `main` (v15) and `version-16` (v16) in step; only `[tool.bench.frappe-dependencies]` should
  differ. Update the "Current Phase" marker here when a phase's acceptance is met.
