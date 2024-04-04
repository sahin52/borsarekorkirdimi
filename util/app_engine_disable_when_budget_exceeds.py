import base64
import json
import os
from googleapiclient import discovery

APP_NAME = "borsarekorkirdimi"

def limit_use_appengine(data, context):
    print("Starting, APP_NAME:",APP_NAME)
    print("GOOGLE_CLOUD_PROJECT(getenv):", os.getenv("GOOGLE_CLOUD_PROJECT"))
    print("GOOGLE_CLOUD_PROJECT:(environ.get)", os.environ.get("GOOGLE_CLOUD_PROJECT"))
    print("GCP_PROJECT(environ.get):",os.environ.get("GCP_PROJECT"))
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
        print("Disabled app:", APP_NAME)
    else:
        print("It is not serving")
