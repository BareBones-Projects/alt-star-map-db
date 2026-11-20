# // ALT DATABASE CONSUMER BRIDGE

Canonical source: [BareBones-Projects/ALT-Database](https://github.com/BareBones-Projects/ALT-Database).

The database owns approved coordinates, locations, media metadata and lore records; this repository remains responsible for its own runtime features. **No direct SQL connections or admin credentials are permitted in this repository's public/client bundle.**

Configure `ALT_DATABASE_URL` in the service or local development environment. Use HTTPS outside localhost. Read endpoint: `/api/v1/entities?kind=star`. Validate response schema/version and stable canonical IDs before replacing local data. Do not infer real coordinates from screen-layout positions.

Current delivery: contract and read adapter scaffolding. Existing UI/runtime data paths remain unchanged until contract testing passes. See the database's `docs/INTEGRATIONS.md` for mapping. Draft and restricted records are never returned to consumers. Admin login remains exclusively with ALT-Database.

### Acceptance checklist

- [ ] Start ALT Database with approved sample records.
- [ ] Test read endpoint against production-compatible HTTPS base URL.
- [ ] Verify schema compatibility and invalid-record handling.
- [ ] Confirm old local mock/fixtures still work when service is unavailable.
- [ ] Confirm no private/unpublished data is accessible.
- [ ] Run existing repo tests and verify runtime implementation.
