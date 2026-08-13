# DEPLOY — subir cambios rápido

> Runbook operativo. Dos mitades independientes: **api** (Cloud Run) y **web** (Cloudflare Pages). Subir una NO requiere subir la otra.

## Subir el backend (api → Cloud Run)
```
cd api
gcloud run deploy scholar-rag-api --source . --region us-east1 --allow-unauthenticated \
  --env-vars-file .env.deploy.yaml --memory 2Gi --cpu 2 --project geosdata --quiet
```
- Buildea el Dockerfile y despliega. Tarda ~2-4 min. La primera request tras subir es lenta (cold start descarga el modelo de embeddings a `/tmp`).
- URL: `https://scholar-rag-api-448285277410.us-east1.run.app`

## Subir la web (front → Cloudflare Pages)
```
# desde la raíz del repo
npx wrangler pages deploy web --project-name scholar-rag --branch main --commit-dirty=true
```
- Sube los archivos de `web/` (estático). Segundos.
- URL: `https://scholar-rag.pages.dev` · panel: `/stats.html`

## Recargar el corpus (si cambian/aumentan las tesis)
```
cd api
uv run python -m scripts.ingest      # idempotente: upsert por tesis
uv run python -m scripts.search "…"  # verificar retrieval
```
La base es Neon (`scholar_rag`), la comparten tu máquina y Cloud Run, así que reindexar desde local ya impacta producción.

## Secretos (`.env.deploy.yaml`)
- Lo consume el deploy del api; está **gitignored** (no viaja al repo).
- Si clonás el repo limpio o falta, regeneralo desde `api/.env`:
```
cd api
python -c "
keep={'DATABASE_URL','GROQ_API_KEY','GROQ_MODEL','EMBEDDING_MODEL'}
out=[]
for l in open('.env',encoding='utf-8'):
    l=l.strip()
    if not l or l.startswith('#') or '=' not in l: continue
    k,v=l.split('=',1)
    if k in keep: out.append((k,v))
out.append(('FASTEMBED_CACHE','/tmp/fastembed'))
open('.env.deploy.yaml','w',encoding='utf-8').write(''.join(f'{k}: \"{v}\"\n' for k,v in out))
"
```
- Mejora futura: mover a Secret Manager (`--set-secrets`) en vez de env-vars-file.

## Cuándo se sube cada cosa
| Cambiaste… | Subí… |
|---|---|
| código Python (`api/app`, `api/scripts`) | api |
| la página (`web/`) | web |
| el corpus / la base | recargar corpus (no requiere redeploy) |
