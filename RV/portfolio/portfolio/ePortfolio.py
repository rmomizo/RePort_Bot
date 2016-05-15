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


def i_collocations(raw):

    tokenizer = WordPunctTokenizer()
    tokens = tokenizer.tokenize(raw)

    bigrams = [(tokens[i], tokens[i +1]) for i in range(len(tokens)-1)]
    collocations = [(t1, t2) for (t1, t2) in bigrams if t1 == "i" or t1 == 'we' or t1 == 'my' or t1 == "our"]

    trigrams = [(tokens[i], tokens[i +1], tokens[i+2]) for i in range(len(tokens)-2)]
    trilocations = [(t1, t2, t3) for (t1, t2, t3) in trigrams if t1 == "i" or t1 == 'we' or t1 == 'my'
                    or t1 == "our"]

    return collocations, trilocations

def you_collocations(raw):

    tokenizer = WordPunctTokenizer()
    tokens = tokenizer.tokenize(raw)

    bigrams = [(tokens[i], tokens[i +1]) for i in range(len(tokens)-1)]
    collocations = [(t1, t2) for (t1, t2) in bigrams if t1 == "you" or t1 == 'your']

    trigrams = [(tokens[i], tokens[i +1], tokens[i+2]) for i in range(len(tokens)-2)]
    trilocations = [(t1, t2, t3) for (t1, t2, t3) in trigrams if t1 == "you" or t1 == 'your']

    return collocations, trilocations

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

    #I voice collocations

    i_col, i_col_tri = i_collocations(combined_pages.lower())
    i_s = []
    for i in range(len(i_col_tri)):
        i_s.append(i_col_tri[i][0])

    i_c = dict(Counter(i_s))
    i_cs = {'i':0, 'my':0, 'our':0, 'we':0}

    for key, value in i_c.items():
        try:
            i_cs[key] = '{0:.2f}'.format(value/len(i_s))
        except ZeroDivisionError:
            i_cs["Null"] = 0

    i_content = defaultdict(list)
    for (x,y,z) in i_col_tri:
        i_content[x].append((x,y,z))

    #You voice collocations
    you_col, you_col_tri = you_collocations(combined_pages.lower())
    y_s = []
    for i in range(len(you_col_tri)):
        y_s.append(you_col_tri[i][0])

    y_c = dict(Counter(y_s))
    y_cs = {'you':0, 'your':0}
    for key, value in y_c.items():
        try:
            y_cs[key] = value(len(y_s))
        except ZeroDivisionError:
            y_cs['Null'] = 0

    you_content = defaultdict(list)
    for (x,y,z) in you_col_tri:
        you_content[x].append((x,y,z))

    with open('results2.html', 'w') as myFile:
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
  <script src="http://code.jquery.com/ui/1.11.4/jquery-ui.js"></script>
    <script>
  $(function() {
    $( ".radio" ).buttonset();
  });


  $(document).ready(function() {
  $("#i-box").css("visibility", "visible");
    $("input[name$='radio']").click(function() {
        var test = $(this).val();

        $(".voice-info").css("visibility", "hidden");
        $("#" + test).css("visibility", "visible");
    });

    $("#you-box").css("visibility", "visible");
    $("input[name$='radioy']").click(function() {
        var testy = $(this).val();

        $(".voice-info-y").css("visibility", "hidden");
        $("#" + testy).css("visibility", "visible");
    });
});
  </script>
  """)

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
</div>

<div id="doughnut-i">
	 <div class="donut">
    	<form>
  			<div class="radio">
    		<input type="radio" id="radio1" value="i-box" name="radio"><label for="radio1" checked="checked">I</label>
    		<input type="radio" id="radio2" value="my-box" name="radio"><label for="radio2">My</label>
    		<input type="radio" id="radio3" value="we-box" name="radio"><label for="radio3">We</label>
      		<input type="radio" id="radio4" value="our-box" name="radio"><label for="radio4">Our</label>
  		</div>
		</form>

    <div id="i-box" class="voice-info">""")

        myFile.write("""<ul>""")
        for item in i_content['i']:
            myFile.write("""<li>""" + str(item) + """</li>""")

        myFile.write("""</ul></div><div id="my-box" class="voice-info">""")

        myFile.write("""<ul>""")
        for item in i_content['my']:
            myFile.write("""<li>""" + str(item) + """</li>""")

        myFile.write("""</ul></div>
    <div id="we-box" class="voice-info">""")

        myFile.write("<ul>")
        for item in i_content['we']:
            myFile.write("""<li>""" + str(item) + """</li>""")

        myFile.write("""</ul></div>
    <div id="our-box" class="voice-info">""")

        myFile.write("""<ul>""")
        for item in i_content['our']:
            myFile.write("""<li>""" + str(item) + """</li>""")

        myFile.write("""</ul></div>
    	</div>
</div>

    <div id="doughnut-y">
    <div class="donut">
    <form>
  		<div class="radio">
    		<input type="radio" id="radio1y" name="radioy" value="you-box"><label for="radio1y">You</label>
    		<input type="radio" id="radio2y" name="radioy" value="your-box" checked="checked"><label
    		for="radio2y">Your</label>

  		</div>
	</form>
    	<div id="you-box" class="voice-info-y">""" + str(you_content['you']) + """</div>
    	<div id="your-box" class="voice-info-y">""" + str(you_content['your']) + """</div>
    	</div>
	</div>
""")
        myFile.write('<h2>h-Point for total pages ' + str(start_url) + ' ' + str((t_h[0].encode('ascii',
                                                                                              errors='ignore'), t_h[1]
                                                                     )) + '</h2>')
        myFile.write('<section class="tree-map"></section>')
        myFile.close()

    with open('results2.html', 'a') as myFile:
        for i in range(len(page_reports)):
            myFile.write("""<h2>""" + titles[i] + """</h2><h2>h-point """ + str(find_h(preprocess(pages[i][1]))) +
                    '''<div id="page-tree''' + str(i) + '''">'''  + "</div>")
        myFile.close()

    with open('results2.html', 'a') as myFile:
        myFile.write('<div id="doughnut-i">'
                     '<div id="i-box"></div>'
                     '<div id="my-box"></div>'
                     '<div id="we-box"></div>'
                     '<div id="our-box"></div>'
                     '</div>'
                     '<div id="doughnut-y">'
                     '<div id="you-box"></div>'
                     '<div id="your-box"></div>'
                     '</div>\n')
        myFile.write('<div class="spacer"></div>')
        # myFile.write('<footer>\n')
        # myFile.write('<p>R<em>ePort</em> Bot | R.M. Omizo</p>')
        # myFile.write('</footer>\n')
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
}

	var wd = ($(window).width() * .8)/2.6;
			var hd = ($(window).width() * .8)/2.6;

			var idata =""" + str([i_cs['i'], i_cs['my'],i_cs['our'],i_cs['we']])  + """;
			var ilabels = ['i', 'my', 'our', 'we'];

			var outerRadius = wd / 2;

			//Set innerRadius value to 0 for standard pie chart
			var innerRadius = wd/3;

			var arc = d3.svg.arc()
					.innerRadius(innerRadius)
					.outerRadius(outerRadius);

			var pie = d3.layout.pie();

			//Custom color range; replace hex codes in array to revise colors
			//Colors will be selected in sequentially in current functions
			var color = d3.scale.ordinal()
			//i, my, our, we
				.range(["#FF92E4 ", "#61CCCB ", "#FFD047", "#B23C7A"]);

			//Create SVG element
			var svg = d3.select("#doughnut-i")
					.append("svg")
					.attr("width", wd)
					.attr("height", hd);

			if (eval(idata.join("+")) == 0) {
			svg.append("text")
				.attr("x", 197)
				.attr("y", 197)
				.attr("text-anchor", "middle")
			    .attr("font-family", "Oxygen")
			    .attr("fill", "#000")
			    .attr("font-size", 150)
			    .text("0%");
		} else {
				var arcs = svg.selectAll("g.arc")
						.data(pie(idata))
						.enter()

						.append("g")
						.attr("class", "arc")

						.attr("transform", "translate(" + outerRadius + "," + outerRadius + ")");

				//Draw arc paths
				arcs.append("path")

						.attr("fill", function (d, i) {
							return color(i);
						})
						//Animated rendering
						.transition()
						.duration(500)
						.attrTween('d', function (d) {
							var i = d3.interpolate(d.startAngle, d.endAngle);
							return function (t) {
								d.endAngle = i(t);
								return arc(d);
							}
						});

				//Labels
				arcs.append("text")

						.attr("transform", function (d) {
							return "translate(" + arc.centroid(d) + ")";
						})
						.attr("text-anchor", "middle")
						.style("z-index", 10)
						.attr("font-family", "Oxygen")
						.attr("fill", "#fff")
						.attr("font-size", 16)


						.text(function (d, i) {
							if (d.value > 0) {
								return String(ilabels[i]) + " : " + String(d.value)
							}
							else {
								return
							}

						});

				arcs.append("text")
						.attr("x", 0)
						.attr("y", 22)
						.attr("text-anchor", "middle")
						.attr("font-family", "Oxygen")
						.attr("fill", "#000")
						.attr("font-size", 100)
						.text("%");
			}


//Width and height for doughnut
			var we = ($(window).width() * .8)/2.6;
			var he = ($(window).width() * .8)/2.6;

			var ydata =""" + str([y_cs['you'], y_cs['your']])  + """;
			var ylabels = ['you', 'your'];

			var outerRadiusY = we / 2;

			//Set innerRadius value to 0 for standard pie chart
			var innerRadiusY = we/3;

			var arcY = d3.svg.arc()
					.innerRadius(innerRadiusY)
					.outerRadius(outerRadiusY);

			var pieY = d3.layout.pie();

			//Create SVG element
			var svgY = d3.select("#doughnut-y")
					.append("svg")
					.attr("width", we)
					.attr("height", he);

			//Set up groups

			if (eval(ydata.join("+")) == 0) {
			svgY.append("text")
				.attr("x", 197)
				.attr("y", 197)
				.attr("text-anchor", "middle")
			    .attr("font-family", "Oxygen")
			    .attr("fill", "#000")
			    .attr("font-size", 150)
			    .text("0%");
		} else {
			var arcsY = svgY.selectAll("g.arcY")
					.data(pieY(ydata))
					.enter()
					.append("g")
					.attr("class", "arc")
					.attr("transform", "translate(" + outerRadiusY + "," + outerRadiusY + ")");


			//Draw arc paths
			arcsY.append("path")
					.attr("fill", function (d, i) {
						return color(i);
					})

					//Animated rendering
					.transition()
					.duration(500)
					.attrTween('d', function (d) {
						var i = d3.interpolate(d.startAngle, d.endAngle);
						return function (t) {
							d.endAngle = i(t);
							return arcY(d);
						}
					})

				//Non-animated rendering
				//.attr("d", arc)
			;

			//Labels
			arcsY.append("text")
					.attr("transform", function (d) {
						return "translate(" + arc.centroid(d) + ")";
					})
					.attr("text-anchor", "middle")
					.style("z-index", 10)
					.attr("font-family", "Oxygen")
					.attr("fill", "#fff")
					.attr("font-size", 12)
					.text(function (d) {
						if (d.value > 0) {
							return d.value
						}
						else {
							return
						}
					});

			//Percentage label
			arcsY.append("text")
					.attr("x", 0)
					.attr("y", 22)
					.attr("text-anchor", "middle")
					.attr("font-family", "Oxygen")
					.attr("fill", "#000")
					.attr("font-size", 100)
					.text("%");
		}

        </script> """)
        myFile.close()

    with open("results2.html", "a") as myFile:
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
    with open('results2.html', 'a') as myFile:
        myFile.write('</body>\n')
        myFile.write('</html>\n')
        myFile.close()



    print "RePort write complete!"
