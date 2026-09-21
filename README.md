## Pakistan Compliance (`pakistan_compliance`)

Pakistan localization for Frappe / ERPNext: FBR-compliant sales tax invoices and other print
formats, the tax setup (federal and provincial sales tax, further tax, withholding tax) with its
Chart of Accounts, withholding-tax handling with filer / non-filer (ATL) awareness, and integration
with FBR's Digital Invoicing system (real-time e-invoicing that returns an Invoice Reference Number
and QR code).

This is a single app. It is the Pakistan counterpart to the KSA localization work (`ksa_print_formats`
and `zatca`).

> Tax rates, thresholds, and the FBR digital-invoicing contract change frequently (annual Finance
> Acts, SROs). This app keeps rates configurable and verifies the FBR integration against the live
> FBR / PRAL sandbox. Always confirm current rules against the official source.

### Compatibility

- ERPNext / Frappe **v15**: use the `main` branch.
- ERPNext / Frappe **v16**: use the `version-16` branch.

### Installation

```bash
cd $PATH_TO_YOUR_BENCH

# ERPNext / Frappe v15
bench get-app <repo-url> --branch main

# ERPNext / Frappe v16
bench get-app <repo-url> --branch version-16

bench --site $YOUR_SITE install-app pakistan_compliance
bench --site $YOUR_SITE migrate
```

### Status

Early development. See `CLAUDE.md` for the phase-by-phase build plan and the current phase marker.

### License

MIT
