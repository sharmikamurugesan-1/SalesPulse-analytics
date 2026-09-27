# Security Policy: SalesPulse-analytics

## 1. Supported Versions
| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## 2. Threat Model & Mitigations

### Tabular Ingestion & CSV Injection Prevention
- **CSV Injection (Formula Injection) Sanitization:** Cells starting with formula triggers (`=`, `+`, `-`, `@`, `|`, `%`) are escaped or stripped when re-exporting tabular reports to prevent arbitrary execution in Microsoft Excel and Google Sheets.
- **Payload Size Control:** File uploads are limited to 25 MB to mitigate server memory exhaustion during dataframe transformations.
- **Schema Strictness:** Non-numeric values in financial columns (`Revenue`, `Profit`, `Units`) are coerced safely or segregated into an unparseable quarantine log rather than executing unchecked expressions.

### SQL Parameterization
- All SQLite queries in `db_loader.py` use named parameter bindings (`:Transaction_ID`, `:Date`, etc.) to prevent SQL injection vulnerabilities.

## 3. Reporting a Vulnerability
To report a vulnerability or data leakage issue, please contact the project maintainer at `sharmika.murugesan@gmail.com`. Disclosures are acknowledged within 24 hours.
