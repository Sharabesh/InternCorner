# InternCorner
* InternCorner was a Intern Stretch Assignment at Cisco Systems designed to track the intern experience. Through the portal Interns have the opportunity to repeatedly "check-in" over the course of their internship - elaborate on how they are feeling and what their situation is. The site also provides a suite of analytics and user engagement functionality designed to maintain a consistent user-base. 

## Technical Details 
* InternCorner is written in Python's tornado framework 
* API Endpoints are designated by \*Endpoint classes while classes designated to rendering HTML files are designated by \*Handler 
* All user data is securely stored in a postgres management portal 
* The website is hosted on heroku at https://interncorner.herokuapp.com

## Check out our Chrome Extension 
* As a tool to expand ease of use InternCorner also has a designated Chrome Extension (InternCorner) on the Chrome app store. This application allows users to quickly check-in. 

## Contributing to InternCorner 
* Clone the github repo 
> git clone https://github.com/Sharabesh/InternCorner.git
* Install the requirements 
> pip install -r requirements.txt
* Run the webapp 
> cd InternCorner 
> python3 app.py
