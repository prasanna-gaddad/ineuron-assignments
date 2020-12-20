from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
# import pymongo
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')


@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ", "")
        try:
            # dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            # db = dbConn['iNeuron']
            # reviews = db[searchString].find({})
            # if reviews.count() > 0:
            # return render_template('results.html', reviews=reviews)
            # else:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            flipkartPage = requests.get(flipkart_url)
            # or
            # uClient = uReq(flipkart_url)
            # flipkartPage = uClient.read()
            # uClient.close()

            flipkart_html = bs(flipkartPage.text, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_2pi5LC col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']

            prodRes = requests.get(productLink)

            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            # table = db[searchString]

            reviews = []

            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except:
                    custComment = 'No Customer Comment'

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}

                # x = table.insert_one(mydict)

                reviews.append(mydict)

            return render_template('results.html',
                                   reviews=reviews[0:(len(reviews) - 1)])  # showing the review to the user
        except:
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
