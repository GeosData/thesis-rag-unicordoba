-- 001_fts_unaccent.sql
-- Full-text search was accent-sensitive: the corpus has "orientación" (accented)
-- but user queries arrive without accents, so websearch_to_tsquery('spanish', ...)
-- matched nothing and hybrid_search silently collapsed to vector-only.
-- Fix: an accent-insensitive text search configuration applied on both sides.

CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TEXT SEARCH CONFIGURATION spanish_unaccent (COPY = spanish);
ALTER TEXT SEARCH CONFIGURATION spanish_unaccent
    ALTER MAPPING FOR hword, hword_part, word WITH unaccent, spanish_stem;

-- Rebuild the generated tsv column with the accent-insensitive configuration.
DROP INDEX IF EXISTS chunk_tsv_idx;
ALTER TABLE chunk DROP COLUMN tsv;
ALTER TABLE chunk ADD COLUMN tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('spanish_unaccent', content)) STORED;
CREATE INDEX chunk_tsv_idx ON chunk USING gin (tsv);

-- retrieval_repository.hybrid_search now uses websearch_to_tsquery('spanish_unaccent', ...)
