from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

# from flask_cors import CORS, cross_origin

app = Flask(__name__)


@app.route('/', methods=['GET'])
# @cross_origin()
def homepage():
    return render_template('index.html')


@app.route('/review', methods=['POST', 'GET'])
# @cross_origin()
def index():
    if request.method == 'POST':
        product = request.form['content'].replace(" ", "")
        try:
            conn_DB = pymongo.MongoClient("mongodb://localhost:27017/")
            DB = conn_DB['iNeuron']
            reviews = DB[product].find({})
            if reviews.count() > 0:
                return render_template('results.html', reviews=reviews)
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + product

                flipkartPage = requests.get(flipkart_url)

                # OR

                # open_url = uReq(flipkart_url)
                # flipkartPage = open_url.read()
                # open_url.close()

                flipkart_html = bs(flipkartPage.text, "html.parser")
                review_list = flipkart_html.findAll("div", {"class": "_2pi5LC col-12-12"})
                del review_list[0:3]
                box = review_list[0]
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']

                prodRes = requests.get(productLink)

                # OR

                # prodRes = uReq(productLink)
                # propage = prodRes.read()
                # prodRes.close()

                prodRes.encoding = 'utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

                table = DB[product]

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

                    mydict = {"Product": product, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}

                    x = table.insert_one(mydict)

                    reviews.append(mydict)

                return render_template('results.html',
                                       reviews=reviews[0:(len(reviews) - 1)])  # showing the review to the user
        except:
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
