# Facebook retrieval

The goal of this project is to retrieve caption, comments and images of each post related to a specific search request on FB.

## Approach:

Since the Graph API does not allow data to be scraped using a Facebook search (it only provides data related to a page, account, group or event), I used Selenium to extract the Facebook search page for a specific search request to capture all the necessary data, and then store it in a Mongodb database (locally).

After retrieving the links of all posts related to the search, the selenium driver locate to each link and captures the caption of the post, the comments if they exist, and the link of the image if it exists.

The last step is to store this data in mongodb using pymongo and mongodbcompass in two collections : *posts* and *fs.files*. The first one stores a list of captions, comments and image links corresponding to each post, and the second one stores the contents of images found using the images links.
## Usage:

To use this tool, please install the requirements by running in the same location of the project the following command :  

```pip install -r requirements.txt```

Note that you need to have Mongodb, MongodbCompass and Chrome installed in your machine.

Locate to the config.py file to set your FB credentials, the search request and the name of your database.

Start scraping by running : 

```python main.py```

## Note and Warning:

**The account used during this process has been banned by FB due to multiple logins. To test this project, you must set new credentials**.  

**Note that your account may be banned after several attempts. Please use a secondary account**