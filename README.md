For developement purpose, you can create a requirements.txt file from the poetry file using the command: 
````
poetry export --without-hashes --format=requirements.txt > requirements.txt
````
You might have trouble isntalling the swagger dependency using pip, to achieve this you need to use the following command :
 
````
pip install git+https://github.com/sladkovm/strava-swagger-client.git
````