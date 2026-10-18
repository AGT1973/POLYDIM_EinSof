import os
import json

# Write a temporary kaggle.json to use this account's credentials
kaggle_dir = os.path.expanduser("~/.kaggle_temp_account3")
os.makedirs(kaggle_dir, exist_ok=True)
kaggle_json = os.path.join(kaggle_dir, "kaggle.json")

with open(kaggle_json, "w") as f:
    json.dump({"username": "polydimcla", "key": "KGAT_4ef61a6e17016965ff828a3615de510c"}, f)
os.chmod(kaggle_json, 0o600)

# Now use the kaggle API directly to get user info
import subprocess
env = os.environ.copy()
env["KAGGLE_CONFIG_DIR"] = kaggle_dir

# Try to get user profile via API call
res = subprocess.run(["python", "-c", """
import os
os.environ['KAGGLE_CONFIG_DIR'] = r'""" + kaggle_dir + """'
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()
print('Authenticated username:', api.config_values.get('username', 'UNKNOWN'))
print('Username from get_config_value:', api.get_config_value('username'))
"""], env=env, capture_output=True, text=True)
print("STDOUT:", res.stdout.strip())
print("STDERR:", res.stderr.strip()[:300])
