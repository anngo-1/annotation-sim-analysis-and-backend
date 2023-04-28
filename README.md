# annotation-sim-analysis-and-backend

This is a flask API meant to be used alongside the annotation simulator for exporting annotation results to google sheet, and analyzing annotator agreement/statistics.

First, run the following commands to install the necessary python packages on your local machine

```
pip install google-api-python-client
pip install google-auth
pip install flask
pip install flask-cors
```
   
HOW TO USE:
1. Clone repo
2. Create a service account with our google cloud project, and download its json credentials.
3. Put the json credential file into the directory of the cloned project
4. Run the file
