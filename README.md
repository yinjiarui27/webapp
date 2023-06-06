# Please install these libraries

# Update APT
sudo apt-get update

# For Sql-client
sudo apt-get install mysql-client

# For python and related frameworks
sudo apt-get install python3
sudo apt-get install python3-flask
sudo apt-get install python3-pymysql
sudo apt-get install python3-boto3

# For entering VM before running the web app
ssh -i ./keypair1.pem ubuntu@18.143.237.131
***Please contact me to get keypair1.pem***

# For running application
sudo python3 Empapp.py