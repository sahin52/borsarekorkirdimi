import base64
import json
import os
from googleapiclient import discovery

APP_NAME = os.getenv("GCP_PROJECT")
if not APP_NAME:
    APP_NAME = os.getenv("GOOGLE_CLOUD_PROJECT")
if not APP_NAME:
    APP_NAME = os.environ.get("GCP_PROJECT")
def limit_use_appengine(data, context):
    print("Starting, APP_NAME:",APP_NAME)
    pubsub_data = base64.b64decode(data["data"]).decode("utf-8")
    pubsub_json = json.loads(pubsub_data)
    cost_amount = pubsub_json["costAmount"]
    budget_amount = pubsub_json["budgetAmount"]
    print("budget_amount:", budget_amount, "cost_amount:", cost_amount, "pubsub_json:", pubsub_json)
    if cost_amount <= budget_amount:
        print(f"No action necessary. (Current cost: {cost_amount})")
        return

    appengine = discovery.build("appengine", "v1", cache_discovery=False)
    apps = appengine.apps()
    print("apps: ", apps)
    # Get the target app's serving status
    target_app = apps.get(appsId=APP_NAME).execute()
    print("target_app: ", target_app)
    current_status = target_app["servingStatus"]
    print("current status: ", current_status)
    # Disable target app, if necessary
    if current_status == "SERVING":
        print(f"Attempting to disable app {APP_NAME}...")
        body = {"servingStatus": "USER_DISABLED"}
        apps.patch(appsId=APP_NAME, updateMask="serving_status", body=body).execute()
    else:
        print("It is not serving")
