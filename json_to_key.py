'''
このpyファイルは"firestore-key.json"をgitの".streamlit/secrets.toml"に書き出すものです
".streamlit/secrets.toml"の内容をstreamlitのsecretに貼り付けてください
一度使った後は、"firestore-key.json"ないし".streamlit/secrets.toml"は削除してください
'''
import toml

output_file = "path1"
with open("path2") as json_file:
    json_text = json_file.read()

config = {"textkey": json_text}
toml_config = toml.dumps(config)

with open(output_file, "w") as target:
    target.write(toml_config)

'''
# Replace:
db = firestore.Client.from_service_account_json("firestore-key.json")

# With:
import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streamlit-reddit")
When you're done, double-check your Streamlit app — everything should work the
'''
