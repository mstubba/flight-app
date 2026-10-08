PROJECT_ID="devops-project-510219"
REPO="mstubba/gcp-demo-prjs"
SA="github-deployer"
SA_EMAIL="$SA@$PROJECT_ID.iam.gserviceaccount.com"

# 0. Włącz potrzebne API
gcloud services enable iamcredentials.googleapis.com sts.googleapis.com \
  artifactregistry.googleapis.com --project=$PROJECT_ID

# 1. Service account dla pipeline'u
gcloud iam service-accounts create $SA --project=$PROJECT_ID \
  --display-name="GitHub Actions deployer"

# 2. Pula tożsamości
gcloud iam workload-identity-pools create github \
  --project=$PROJECT_ID --location=global \
  --display-name="GitHub Actions Pool"

# 3. Provider wpuszczający tylko Twoje repo
gcloud iam workload-identity-pools providers create-oidc flight-app \
  --project=$PROJECT_ID --location=global \
  --workload-identity-pool=github \
  --display-name="flight-app repo" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == '$REPO'"

# 4. Pozwól repo działać jako service account
POOL_ID=$(gcloud iam workload-identity-pools describe github \
  --project=$PROJECT_ID --location=global --format="value(name)" | tr -d '\r')
echo "POOL_ID=$POOL_ID"

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --project=$PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/$POOL_ID/attribute.repository/$REPO"

# 5. Uprawnienia: push obrazów + deploy na GKE
for ROLE in roles/artifactregistry.writer roles/container.developer; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" --role=$ROLE --condition=None
done

# 6. Repozytorium w Artifact Registry
gcloud artifacts repositories create flight-app \
  --repository-format=docker --location=europe-central2 --project=$PROJECT_ID

# 7. Wartość do gcp.env
gcloud iam workload-identity-pools providers describe flight-app \
  --project=$PROJECT_ID --location=global \
  --workload-identity-pool=github --format="value(name)"