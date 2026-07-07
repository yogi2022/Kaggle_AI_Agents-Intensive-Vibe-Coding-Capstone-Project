# Deploying Berean (course Days 1 & 5)

Berean has two deployable surfaces. Either satisfies the rubric's "deployability".

## A. Frontend + agent on Cloud Run (simplest)
The root `Dockerfile` packages the FastAPI UI, the ADK agent, and the Scripture MCP
server (launched in-process over stdio). With the Google Cloud Starter Tier you can
publish without a billing account (course FAQ 1.2).

```bash
gcloud run deploy berean \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_KEY,GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

## B. ADK agent on Agent Runtime via Agents CLI (Day 5 enterprise path)
`root_agent` lives in `berean_agents/orchestrator.py`. Package and deploy it with the
Agents CLI, then point a Cloud Run frontend at it. Outline (verify exact flags against
current `agents-cli` / Agent Runtime docs):

```bash
agents deploy --agent berean_agents.orchestrator:root_agent --target agent-runtime
```

## Observability
Enable Cloud Trace; ADK emits OpenTelemetry traces so you can inspect the
triage -> specialists -> synthesizer trajectory and the MCP tool calls (Day 4).

## Cleanup
Run `deploy/cleanup.sh berean us-central1` when done; delete API keys; confirm billing
is clear.
