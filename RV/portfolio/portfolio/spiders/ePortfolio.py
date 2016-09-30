from __future__ import division
import requests
import numpy as np
import nltk, re, os
from collections import Counter
from nltk.tokenize import word_tokenize, TreebankWordTokenizer, WordPunctTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
import cPickle, bleach, json
from nltk.tokenize import word_tokenize, TreebankWordTokenizer, WordPunctTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from hindex import *
from collections import defaultdict
from urllib2 import *



stopwords = ['im', '...', 'also', 'mr', 'mrs', 'when', 'me', 'myself', 'ours', 'ourselves', 'that',
             'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
             'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
             'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
             'doing', 'a', 'an', 'the', 'and', 'but', 'or', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
             'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
             'from', 'do', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
             'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
             'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', "'", '"', 'just', 'don', 'now',
             "they're", "'re", "you're", "we're", "'ve", "'s", 'em', 'dy', "'ve", '.', ',', 'th', 'us',
             'wasnt',
             'isnt', ')', '(', '..', 'i.e.', 'googleanalytics']

def flatten_list(somelist):
        if any(isinstance(el, list) for el in somelist) == False:
                return somelist
        flat_list = list(itertools.chain(*somelist))
        return flat_list

def preprocess(raw):
    norm = raw.decode('ascii', 'ignore')
    #norm = r.decode('ascii', 'ignore')
    tokens = WordPunctTokenizer().tokenize(norm)

    #remove stopwords from text using pickled stopwords list
    important_words = [word.lower() for word in tokens if word.lower() not in stopwords and len(word) > 2]

    #stems source text with WordNet Lemmatizer
    lmtzr = WordNetLemmatizer()
    sentences = [lmtzr.lemmatize(w) for w in important_words]

    return sentences

def read_json(filename):
    with open(filename) as data_file:
        data = json.load(data_file)

    return data

def parse_json(filename):
    data = read_json(filename)
    links = data[0]['links']
    start_url = data[0]['start_url']
    pages = []
    for d in data:
        pages.append((d['title'], bleach.clean(d['content'][0],  tags=[], attributes={},styles=[],
                                               strip=True).lstrip()))

    spages = [(p[0], re.subn('\\n', ' ', p[1])[0]) for p in pages]
    spg = [(s[0], s[1].encode('ascii', errors='ignore')) for s in spages]
    return links, spg, start_url

def get_key(item):
    return item[1][1]

def h_report(raw):
    p = preprocess(raw)
    h = find_h(p)
    h_point = (h[0],h[1],('#FFE979'))
    syns = [(x,y,'#5DB2B1') for (x,y) in fast_h(p)]
    auto =  [(x,y,'#B2559B') for (x,y) in slow_h(p)]
    terms = sorted(syns, key=get_key) + sorted(auto, key=get_key)

    return h_point, terms, p

def h_report_page(raw):
    p = preprocess(raw)
    h = find_h(p)
    h_point = (h[0],h[1],('#FFE979'))
    syns = [(x,y,'#5DB2B1') for (x,y) in fast_h(p)]
    auto =  [(x,y,'#B2559B') for (x,y) in slow_h(p)]
    terms = sorted(syns, key=get_key) + sorted(auto, key=get_key)

    tf = []
    for term in terms:
        if term[0] == h_point[0]:
            tf.append(h_point)
        else:
            tf.append(term)

    data = defaultdict(list)
    children = []

    for item in tf:
        children.append({"term" : str(item[0]), "frequency": item[1][0], "rank":item[1][1],
                         "color": item[2]})

    data["name"] = "tree"
    data["children"] = children
    return dict(data)

def make_report(filename):

    links, pages, start_url = parse_json(filename)
    combined_pages = str(pages)
    titles = [p[0][0].encode('ascii', errors='ignore') for p in pages]

    page_reports = []
    for index, p in enumerate(pages):
        page_reports.append((titles, h_report_page(p[1]), index))


    t_h, terms, p = h_report(combined_pages)
    d = find_h_index(p)

    pwc = str(len(word_tokenize(combined_pages)))
    awc = str(np.mean([len(word_tokenize(page[1])) for page in pages]))
    psc = str(len(PunktSentenceTokenizer().tokenize(combined_pages)))

    tf =[]
    for item in terms:
        if item[0] == t_h[0]:
            tf.append(t_h)
        else:
            tf.append(item)

    children = []
    for item in tf:
        children.append({"term" : str(item[0]), "frequency": item[1][0], "rank":item[1][1], "color": item[2]})

    data = defaultdict(list)
    data["name"] = "tree"
    data["children"] = children
    tree = dict(data)


    with open('results3.html', 'w') as myFile:
        myFile.write('<!doctype html>\n')
        myFile.write('<html>\n')
        myFile.write('<head>\n')
        myFile.write('<meta charset="utf-8">\n')
        myFile.write('<meta name="description" content="ePortfolio Analysis Results">\n')
        myFile.write('<meta name="author" content="RePort Bot | R.M. Omizo">\n')
        myFile.write('<title>RePort Bot Results</title>\n')
        myFile.write('<script src="https://d3js.org/d3.v3.min.js" charset="utf-8"></script>')
        myFile.write('<link rel="stylesheet" type="text/css" href="report.css">')
        myFile.write("""  <link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">
  <script src="http://code.jquery.com/jquery-1.10.2.js"></script>
  <script src="http://code.jquery.com/ui/1.11.4/jquery-ui.js"></script> """)

        myFile.write('</head>\n')
        myFile.write('<body>\n')
        myFile.write('<div id="container">\n')
        myFile.write('<header>\n')
        myFile.write('<h1>R<em>ePort</em> Results:' + str(start_url) + '</h1></header>')

        myFile.write("""
        <div id="basic-stats">
<h1>Descriptive Statistics</h1>
<h3>Portfolio Word Count: """ + pwc + """</h3>
<h3>Portfolio Sentence Count: """ + psc + """</h3>
<h3>Average Word Count Per Page: """ + awc + """</h3>
</div>""")


        myFile.write('<h2>h-Point for total pages ' + str(start_url) + ' ' + str((t_h[0].encode('ascii',
                                                                                              errors='ignore'), t_h[1])) + '</h2>')
        myFile.write('<section class="tree-map"></section>')
        myFile.close()

    with open('results.html', 'a') as myFile:
        for i in range(len(page_reports)):
            myFile.write("""<h2>""" + titles[i] + """</h2><h2>h-point """ + str(find_h(preprocess(pages[i][1]))) +
                    '''<div id="page-tree''' + str(i) + '''">'''  + "</div>")
        myFile.close()

    with open('results3.html', 'a') as myFile:

        #myFile.write('<div class="spacer"></div>')
        myFile.write('<footer>\n')
        myFile.write('<p>R<em>ePort</em> Bot | R.M. Omizo</p>')
        myFile.write('</footer>\n')
        myFile.write("""
        <script>
        var tree = """ + str(tree) + """

                  var width = 960,
    height = 600,
    color = d3.scale.category20c(),
    div = d3.select(".tree-map").append("div")
       .style("position", "relative");

var treemap = d3.layout.treemap()
    .size([width, height])
    .sticky(true)
        .sort(function(a,b) { return a.frequency - b.frequency; })
    .value(function(d) { return d.frequency; });

var node = div.datum(tree).selectAll(".node")
      .data(treemap.nodes)
    .enter().append("div")
      .attr("class", "node")
      .call(position)
      .style("background-color", function(d) {
          return d.name == "tree" ? '#fff' : d.color; })
      .attr("title", function(d) { return d.term + ": " + d.frequency;});
       //.attr("class", "tooltip")
        //.text(function(d) { return d.term + ": " + d.frequency;}).call(position);

        node.data(treemap.value(function(d) { return d.frequency; }).nodes);


              $(function() {
    $(document).tooltip();
  });

function position() {
  this.style("left", function(d) { return d.x + "px"; })
      .style("top", function(d) { return d.y + "px"; })
      .style("width", function(d) { return Math.max(0, d.dx - 1) + "px"; })
      .style("height", function(d) { return Math.max(0, d.dy - 1) + "px"; });
}</script>""")

    with open("results.html", "a") as myFile:
        for index, p in enumerate(page_reports):
            myFile.write("""<script>
    div = d3.select(""" + '''"#page-tree''' + str(index) + '''"''' + """).append("div")
    .attr("class", "tree-map")
       .style("position", "relative");

var tree""" + str(index) + """ = """ + str(p[1]) + """;

var treemap""" + str(index) + """ = d3.layout.treemap()
    .size([width, height])
    .sticky(true)
        .sort(function(a,b) { return a.frequency - b.frequency; })
    .value(function(d) { return d.frequency; });

var node = div.datum(tree""" + str(index) +""").selectAll(".node")
      .data(treemap""" + str(index) + """.nodes)
    .enter().append("div")
      .attr("class", "node")
      .call(position)
      .style("background-color", function(d) {
          return d.name == "tree" ? '#fff' : d.color; })
      .attr("title", function(d) { return d.term + ": " + d.frequency;});
       //.attr("class", "tooltip")
        //.text(function(d) { return d.term + ": " + d.frequency;}).call(position);

        node.data(treemap""" + str(index) + """.value(function(d) { return d.frequency; }).nodes);


              $(function() {
    $(document).tooltip();
  });

        </script>""")
        myFile.close()
    with open('results3.html', 'a') as myFile:
        myFile.write('</body>\n')
        myFile.write('</html>\n')
        myFile.close()



    print "RePort write complete!"
