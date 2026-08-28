"""Repo-compat shim: the audit engine's single source is
deadwood_audit.core (pre-PyPI namespace flattening, D25). This
package exists so the frozen experiment record keeps importing
`auditor.*` unchanged; it is not part of the published wheel."""
