# coding=utf-8

# A standalone webpage with formatting for pretty reading. Compare to HTML for more unadorned output.

import renderer
import re
import fileio

class RendererWeb(renderer.Renderer):

	def render(self):
		print "Rendering to standalone webpage."
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		pass

	def makeOutputFile(self):
		self.collapsedText = prepForHTMLOutput(self.collapsedText)
		workFile = self.renderFormattingSequences(self.params)
		workFile = specialHTMLFixes(workFile)
		postHTMLificationSanityCheck(workFile)
		workFile = addHeaderAndFooter(workFile, self.params.fileId)
		outputFileName = "%s%s.html" % (self.params.outputDir, self.params.fileId)
		fileio.writeOutputFile(outputFileName, workFile)

	def suggestEndMatters(self):
		return ["end-stats.txt", "end-abouttheauthor.txt"];

	def renderFormattingSequence(self, contents, renderParams):
		# NOTE we can't include quoted things like style classes here because they'll get converted to smart quotes!
		code = contents[0]
		if code == "part":
			partNum = contents[1]
			partTitle = contents[2]
			return "<h2>" + partNum + ": " + partTitle + "</h2><p>&nbsp;</p>"
		if code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			return "<blockquote>\n" + epigraph + "</blockquote><blockquote><p><i>" + source + "</i></p>\n</blockquote><p>&nbsp;</p>"
		if code == "end_part_page":
			return "<p>&nbsp;</p>"
		if code == "chapter":
			chapNum = contents[1]
			intro = "" if chapNum == "EPILOGUE" else ""
			return ("""<h3 id="chap_%s">""" % chapNum) + intro + chapNum + "</h3>" 
		if code == "section_break":
			return "<hr>"
		if code == "verse":
			text = contents[1]
			return "<blockquote><i>" + text + "</i></blockquote>"
		if code == "verse_inline":
			text = contents[1]
			return "\n<i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + text + "</i>\n"
		if code == "verse_inline_sc":
			text = contents[1]
			return "\n<p><span class=sc>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + text + "</span></p>\n"
		if code == "pp":
			return "</p><p>"
		if code == "i":
			text = contents[1]
			return "<i>" + text + "</i>"
		if code == "b":
			text = contents[1]
			return "<b>" + text + "</b>"
		if code == "sc" or code == "scwide":
			text = contents[1]
			return "<span class=sc>" + text + "</span>"
			# return text.upper()
		if code == "vspace":
			# TODO: Make this work if there's a need.
			return "<p>&nbsp;</p>"
		if code == "endmatter" or code == "start_colophon":
			title = contents[1]
			return "<p>&nbsp;</p><h2>" + title + "</h2>"
		if code == "columns" or code == "end_columns":
			return ""
		if code == "url":
			url = contents[1]
			return url
		if code == "finish_colophon":
			return ""



		raise ValueError("Unrecognized command '%s' in control sequence '%s'" % (code, contents)) 


def prepForHTMLOutput(text):
	# Fixes that need to happen before we expand formatting sequences.

	# Remove space at start of lines (before formatter adds any)
	text = re.sub(r"\n[ \t]*", "\n", text)

	return text

def specialHTMLFixes(text):
	# Fixes that should happen after all output is rendered.
	# Fix unicode quotes and special chars
	text = re.sub(r"'", "&rsquo;", text)
	text = re.sub(r"’", "&rsquo;", text)
	text = re.sub(r"‘", "&lsquo;", text)
	text = re.sub(r"“", '&ldquo;', text)
	text = re.sub(r"”", '&rdquo;', text)
	text = re.sub(r"…", "...", text)
	text = re.sub(r"—", "&mdash;", text)
	text = re.sub(r"---", "&mdash;", text)
	text = re.sub(r"aaronareed\.net", "<a href='https://www.aaronareed.net/'>aaronareed.net</a>", text)

	# Convert Latex explicit line break markers
	text = re.sub(r"\\\\", "<br>", text)

	# Fix single spaces at start of new lines (we can't get rid of these earlier because we might have a tag like {pp} we haven't processed yet, but we only look for single spaces to avoid removing epigraph indents.)
	text = re.sub(r"\n (\w)", r"\n\1", text)

	# Fix line breaks in the middle of sentences.
	text = re.sub(r"\n([a-z])", r" \1", text)

	# Convert to paragraphs.
	lines = text.split('\n')
	output_lines = []
	for line in lines:
		valid_line = len(line) > 0
		if valid_line and line[0] == "<" and line[1] != "i":
			valid_line = False
		if valid_line:
			output_lines.append("<p>" + line + "</p>")
		else:
			output_lines.append(line)
	# text = re.sub(r"\n(.*)\n", r"<p>\1</p>\n\n", text)
	text = '\n\n'.join(output_lines)

	return text

def postHTMLificationSanityCheck(text):
	# Look for unexpected characters etc. here
	pos = text.find('{')
	if pos is not -1:
		raise ValueError("Found invalid underscore '{' character on line %d:\n%s" % (result.find_line_number(text, pos), result.find_line_text(text, pos)) )

def addHeaderAndFooter(text, seed):
	# Bind into a website and stylesheet wrapper.
	header = """
<!doctype html>
<html lang="en">
<head>
<title>Subcutanean %s</title>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="author" content="Aaron A. Reed">
<meta name="viewport" content="width=device-width,initial-scale=1.0" />

<!-- Primary Meta Tags -->
<meta name="title" content="Subcutanean %s" />
<meta name="description" content="A horror novel of parallel realities where no two copies are the same." />

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website" />
<meta property="og:url" content="https://subcutanean.textories.com/books/%s.html" />
<meta property="og:title" content="Subcutanean %s" />
<meta property="og:description" content="A horror novel of parallel realities where no two copies are the same." />
<meta property="og:image" content="https://subcutanean.textories.com/images/square-logo-1024.jpg"/>

<!-- Twitter -->
<meta property="twitter:title" content="Subcutanean %s" />
<meta property="twitter:description" content="A horror novel of parallel realities where no two copies are the same." />
<meta name="twitter:image" content="https://subcutanean.textories.com/images/subcutanean2x1.jpg" />
<meta name="twitter:url" content="https://subcutanean.textories.com/" />
<meta name="twitter:card" content="summary_large_image" />

<!-- google fonts preconnect -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..800;1,400..800&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap" rel="stylesheet">

<style>
	body {
		font-family: "EB Garamond", serif;
		font-optical-sizing: auto;
		font-weight: <weight>;
		font-style: normal;

	}
	#main-content {
	    font-size: 1.2em;
		max-width: 26em;
		margin-left: auto;
		margin-right: auto;
    }
    h1 {  
	    text-transform: uppercase;
        font-size: 55px;
		font-weight: 100;
	    letter-spacing: 5px;
	    text-align: center;
	    margin-bottom: 0px;
    }
    h2 {  
	    font-size: 35px;
		font-weight: 400;
	    letter-spacing: 5px;
	    text-align: center;
	    padding-top: 4em;		        
    }
    h3 {  
		text-align: center;
		padding-top: 3em;
		font-size: 35px;
		padding-bottom: 1em;
		font-weight: 200;
    }
    #author, #seed {
    	text-align: center;
	}
	#seed {
		letter-spacing: 60%%;
		font-weight: bold;
		margin-top: 0;
	}
	#author {
		text-transform: uppercase;
		font-weight: bold;	
		margin-top: 10%%;
		margin-bottom: 20%%;
	}
	.sidebar {
		width: 15%%;
	    position: fixed;
	    left: 1%%;
	    top: 1%%;
	    height: 98%%;
	}
	hr {
		margin-top: 9%%;
		margin-bottom: 9%%;
		width: 20%%;
		opacity: 25%%;	
	}
	.sc {
		font-variant: all-small-caps;
		letter-spacing: 5%%;
	}
	ul {
		list-style: none; 
		padding-left: 0.5em; 
	}
	a, .gray {
		color: gray; 
		text-decoration: none; 
	}

	a:visited {
		color: gray; 
	}

	@media (max-width: 768px) { 
	  div.sidebar {
	    position: static; 
	    width: 100%%; 
	    height: auto; 
	    overflow-y: hidden; 
	    margin-bottom: 20px; 
	  }

	  div.main-content {
	    margin-left: 0; 
	  }

	  h1, h2 {
	  	font-size: xx-large;
	  }
	}

</style>

</head>
<body>

<div class="sidebar">
	<p class="sidebarTitle">Seed %s</p>
	<!--<button>Switch Seeds</button>-->
	<p class="gray"><i>Jump to</i>: 
	<a href="#booktop">Top</a> &bull; <a href="#chap_1">1</a> &bull; <a href="#chap_2">2</a> &bull; <a href="#chap_3">3</a> &bull; <a href="#chap_4">4</a> &bull; <a href="#chap_5">5</a> &bull; <a href="#chap_6">6</a> &bull; <a href="#chap_7">7</a> &bull; <a href="#chap_8">8</a> &bull; <a href="#chap_9">9</a> &bull; <a href="#chap_10">10</a> &bull; <a href="#chap_11">11</a> &bull; <a href="#chap_12">12</a> &bull; <a href="#chap_13">13</a> &bull; <a href="#chap_14">14</a> &bull; <a href="#chap_15">15</a> &bull; <a href="#chap_16">16</a> &bull; <a href="#chap_17">17</a> &bull; <a href="#chap_EPILOGUE">Epilogue</a>
	</p>

	<button id="readmode">Dark Mode</button> 
	<button id="increaseSize">&plus;</button> 
	<button id="decreaseSize">&minus;</button>

	<br/><br/>
	<a href="%s.epub">%s EPUB</a><br/><br/>
	<a href="https://subcutanean.textories.com/">Random Seed Softcover</a><br/>

</div>

<div id="main-content">

<p id="booktop"></p>
<div class="title">
<h1>Subcutanean</h1>
<p id="seed">%s</p>
<p id="author">by Aaron A. Reed</p>
</div>


<div id="frontmatter">

<p>This edition of <i>Subcutanean</i> was generated from seed #%s. Words, sentences, or whole scenes may appear in this rendition but not in others, or vice versa. No two seeds produce identical text.</p>

<p>But all of them are the same story, more or less. Don't worry about what's in the other versions. They don't matter. This is the one you clicked on.</p>

<p>This is the one that's happening to you.</p>

<!--<p><a href="https://subcutanean.textories.com">subcutanean.textories.com</a></p> -->

</div>


  <script>
    const readModeButton = document.getElementById('readmode');
    let isReadMode = false;
    const increaseBtn = document.getElementById('increaseSize');
    const decreaseBtn = document.getElementById('decreaseSize');
    let currentSize = 1.2; // Initial size is 100%%
    const mainText = document.getElementById('main-content');

    readModeButton.addEventListener('click', () => {
      if (isReadMode) {
        document.body.style.backgroundColor = 'white';
        document.body.style.color = 'black';
        readModeButton.textContent = "Dark Mode";
      } else {
        document.body.style.backgroundColor = 'black';
        document.body.style.color = 'white';
        readModeButton.textContent = "Light Mode";
      }
      isReadMode = !isReadMode; 
    });

    increaseBtn.addEventListener('click', () => {
      currentSize *= 1.1; // Increase size by 10%%
      mainText.style.fontSize = currentSize + "em"; 
    });

    decreaseBtn.addEventListener('click', () => {
      currentSize /= 1.1; // Decrease size by 10%%
      mainText.style.fontSize = currentSize + "em"; 
    });

  </script>


""" % (seed, seed, seed, seed, seed, seed, seed, seed, seed, seed)

	footer = """


</div>
</body>
</html>
"""
	return header + text + footer

