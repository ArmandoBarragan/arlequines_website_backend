# Arlequines backend website
This project contains every lambda function used in the backend for the Arlequines website.
## Development
First you need to install docker, if you don't have it installed already, as well as node.js. If you do, then all you need to do now is execute the following commands:</br>
<code>
docker pull amazon/dynamodb-local
npm install
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
serverless login
source ./create_tables.sh
</code></br>
To test the functions, you can just execute <code>run_tests.py</code>. If you want to test a specific endpoint, you can execute <code>sls invoke local</code> or <code>sls invoke local -path path/to/file --function function_name</code>, in case you want to test one of the files in tests that require form data.
