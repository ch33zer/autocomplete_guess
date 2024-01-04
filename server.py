from flask import Flask, request, jsonify
import requests
import urllib.parse
import json
import re

app = Flask(__name__, static_folder="static")

DEBUG = False

def debug_print(*args, **kwargs):
	if DEBUG:
		print(*args, **kwargs)
@app.route('/get_completions/<prompt>', methods=['GET'])
def complete(prompt):
	prompt = prompt.lower().strip()
	debug_print(prompt)
	# Sample:
	# )]}'
  # [[["foo bar",0,[512,433,131]],["foo bar\u003cb\u003e baz\u003c\/b\u003e",0,[512]],["foo bar\u003cb\u003e baz list\u003c\/b\u003e",0,[512]],["foo bar\u003cb\u003e google\u003c\/b\u003e",0,[512]],["foo bar melbourne",46,[175,199,512],{"lm":[],"zh":"foo bar melbourne","zi":"Foo Bar Cocktail Lounge · Melbourne, FL","zp":{"gs_ssp":"eJzj4tZP1zcsKa4szMnOMmC0UjWosLBISTU0tEg2SUs0T7M0t7QyqDA1TTJMNDExS0wxNjY3MEjyEkzLz1dISixSyE3NScovLcpLBQDz8xWs"},"zs":"https://lh5.googleusercontent.com/p/AF1QipNDmykQW5-aUKTl3dc-qKhoAUu_sflsF6CU2d5x\u003dw160-h160-n-k-no"}],["foo bar movie",46,[512],{"lm":[],"zh":"foo bar movie","zi":"FUBAR \u2014 2002 film","zp":{"gs_ssp":"eJzj4tTP1Tcws0gvyjFg9OJNy89XSEosUsjNL8tMBQBlIQgj"},"zs":"https://encrypted-tbn0.gstatic.com/images?q\u003dtbn:ANd9GcSuHCli8oySd5WWGWmPMQEBNMZ1KuZn52b1nU2Q3KsOZwi1YRsaQGANFQnKxA\u0026s\u003d10"}],["foo bar\u003cb\u003e coding\u003c\/b\u003e",0,[512]],["foo bar\u003cb\u003es designs\u003c\/b\u003e",0,[512]],["foo bar\u003cb\u003e baz origin\u003c\/b\u003e",0,[512]],["foo bar\u003cb\u003e baz meaning\u003c\/b\u003e",0,[512]]],{"ag":{"a":{"40024":["","",1,20]}},"q":"JKBrPjRLAkfDCJ6aQBzT8ve8fYg"}]
	num_completions = request.args.get('completions', 3, int)

	r = requests.get(f"https://www.google.com/complete/search?q={urllib.parse.quote_plus(prompt)}&client=gws-wiz&xssi=t")
	r_str = r.text
	r_str = "\n".join(r_str.splitlines()[1:]) # remove weird first line
	debug_print(r_str)
	r_obj = json.loads(r_str)
	r_obj = r_obj[0] # second array element has weird stuff
	debug_print(r_obj)
	stripped = [re.sub('<[^<]+?>', '', resp[0]) for resp in r_obj] # strip out <b></b> tags
	debug_print(stripped)
	lower = [completion.lower() for completion in stripped] # lowercase each entry for case insensitive matching
	debug_print(lower)
	normalize_spaces = [" ".join(completion.split()) for completion in lower] # remove duplicate spaces that may have been left over from previous steps
	debug_print(normalize_spaces)
	has_phrase = [completion for completion in normalize_spaces if prompt in completion] # only keep completions where the prompt is entirely present
	debug_print(has_phrase)
	completion_only = [completion[completion.index(prompt) + len(prompt):].strip() for completion in has_phrase] # strip out the prompt
	debug_print(completion_only)
	no_empty = [completion for completion in completion_only if completion.strip()] # only keep non-empty completions
	debug_print(no_empty)
	final = no_empty[:num_completions] # only keep first N completions
	print(f"{prompt} -> {final}")
	return jsonify(final)

@app.route('/', methods=['GET'])
def index():
	return app.send_static_file("index.html")

if __name__ == '__main__':
   app.run(debug=DEBUG)