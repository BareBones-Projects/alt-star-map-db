# ALT Autonomous Map Data Contract v1 (proposal)

Status: integration branch; requires CI and owner review before production. No canonical scientific or ALT canon data may be invented.

## Ownership
- alt-star-map-db: imported scientific star identity, source observations, reference frames and provenance; never silently transform local light-year positions into fictional parsec positions.
- alt-cyclus-map: deterministic planetary generation and derived texture/image manifests; generated data is provisional until validated.
- alt-void-cartography: ALT fictional sector, HEX and route overlays; do not claim recovered source assets exist.
- ALT-Database: intended canonical validation and snapshot publisher, subject to verifying its live repository and API.
- ALT-celestial-map-web: read-only web renderer; no authoritative coordinate writes.
- ALT-celestial-map-unreal-engine: read-only runtime adapter; UE actor positions are camera/origin-relative, not astronomical source coordinates.
- ALT-hub-ui-master: primary HUD consumer; never source of scientific or planetary truth.

## Required record fields
schema_version, object_id, object_type, parent_id (nullable), coordinate_frame, coordinate_epoch, coordinate_unit, xyz (nullable pending validation), provenance, canon_status, revision, image_manifest (nullable), image_sha256 (nullable).

## Rules
1. Stable IDs; uniqueness and referential integrity; no mixing local solar, galactocentric, ALT fictional or Unreal centimeter frames.
2. Scientific observations, procedural derivations, fictional canon, and player discovery state are separate namespaces. Missing values stay null, not fabricated.
3. Use immutable versioned snapshots with SHA-256 and rollback. Consumers pin snapshot revisions; never auto-edit source code or approved canon.
4. Preview images and texture outputs are generated reproducibly from approved seeds and inputs; store heavy assets outside Git source history; include generation version, source license, hash and color-space metadata.
5. Web uses CDN-compressed preview assets (e.g. WebP/KTX2); UE imports authored source textures into native streaming texture formats. Do not treat web preview as game-quality PBR.
6. Read-only authenticated public API with server-side authorization for classified/discovery state; no admin secrets in clients.
7. CI must test schemas, frame conversion, parent links, texture dimensions/channels, deterministic generation, missing-source negative cases and API compatibility before publishing.
8. Automation may produce draft artifacts and PRs, but publication requires passing validation. Failure preserves last-known-good snapshot. Scheduled jobs must be idempotent and concurrency-safe.
9. Test 100 verified objects end-to-end in web and UE before expanding to larger catalogs. UE engine compilation and gameplay tests are separate release gates.
10. No automatic merges into main until required CI passes and conflicts are resolved.

## Image pipeline interface
Input: approved planet ID, seed, radius, surface class, source/canon revision, optional authored masks.
Output: preview.webp, albedo.png (sRGB), normal.png (linear), roughness.png (linear), optional emissive/cloud layers, manifest.json containing hashes and dimensions. Synthetic outputs must be labeled procedural, not scientific observation.

## Rollout
Stage 1: schema and generator tests. Stage 2: draft generated image artifacts and manifests. Stage 3: canonical validation and snapshot publishing. Stage 4: web and UE runtime integration, cache fallback, load testing. Do not mark later stages deployed without evidence.

BareBones Projects, Designed by: Justin Levesque-Welsch
