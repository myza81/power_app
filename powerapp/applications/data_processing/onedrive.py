from msal import PublicClientApplication
import requests



client_id = "<YOUR_APP_CLIENT_ID>"
tenant_id = "<YOUR_TENANT_ID>"
authority = f"https://login.microsoftonline.com/{tenant_id}"
scopes = ["Files.Read"]

app = PublicClientApplication(client_id, authority=authority)
result = app.acquire_token_interactive(scopes=scopes)
token = result["access_token"]

# ---- Read file from OneDrive ----
file_id = "<ONEDRIVE_FILE_ID>"
url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"

headers = {"Authorization": f"Bearer {token}"}
response = requests.get(url, headers=headers)

# Load into memory (not saved to disk)
file_bytes = BytesIO(response.content)

# ---- Use Pandas directly on memory buffer ----
df = pd.read_excel(file_bytes)
print(df)