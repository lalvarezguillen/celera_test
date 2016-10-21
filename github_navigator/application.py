from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

@app.route("/navigator", methods=["GET"])
def handle_search():
    if "search_term" in request.args:
        search_results = GithubNavigator.search_repos(
            request.args["search_term"])
            
        assert type(search_results) == list
        
        return render_template(
            "template.html",
            search_term = request.args["search_term"],
            search_results = search_results
        )
        
        
        
class GithubNavigator(object):
    search_pattern = "https://api.github.com/search/repositories?q={}"
    headers = {"User-Agent":"lalvarezguillen@github"}
    
    @classmethod
    def search_repos(cls, search_term):
        search_string = cls.search_pattern.format(
            search_term)
            
        r = requests.get(search_string, headers=cls.headers)
        if r.status_code == 200:
            response = json.loads(r.content.decode("utf-8"))
            if response["items"]:
                ordered_results = cls.filter_for_celera(response["items"])
                return cls.include_indexes(ordered_results)
            else:
                return response["items"]
      
            
    @classmethod        
    def filter_for_celera(cls, results_list):
        results_list = sorted(results_list,
            key=lambda x: x["created_at"],
            reverse=True
        )
        return results_list[:5]
        
        
    @classmethod
    def include_indexes(cls, results_list):
        for i, result in enumerate(results_list):
            result["index"] = i+1
        return results_list
            

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)