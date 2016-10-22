from flask import Flask, render_template, request
import requests
import json
import click

app = Flask(__name__)

@app.route("/navigator", methods=["GET"])
def handle_search():
    """
    @description: Simple endpoint to handle users' queries.
    """
    # If a query term was provided, search for repos matching the query
    if "search_term" in request.args:
        search_results = GithubNavigator.search_repos(
            request.args["search_term"])
            
        assert type(search_results) == list
    
    # And include on each repo's info, data related to its last commit.        
        search_results = [
            GithubNavigator.include_last_commit_info(repo_info)
            for repo_info in search_results
            ]
        
    # Then render the collected info, on the template.
        return render_template(
            "template.html",
            search_term = request.args["search_term"],
            search_results = search_results
        )
    
    # Handle the scenario where no query was provided    
    return "Include a search term in your query!"
        
        
        
class GithubNavigator(object):
    """
    @description: Very simple class to encapsulate the tools that perform
    the querying, and data processing.
    """
    search_pattern = "https://api.github.com/search/repositories?q={}"
    # github's docs suggest including something like this, for UA header.
    headers = {"User-Agent":"lalvarezguillen@github"}
    
    @classmethod
    def search_repos(cls, search_term):
        """
        @description: Main querying routine.
        @arg search_term: {str} The term to query GitHub's API with.
        @return: {list} Contains a dictionary per repository encountered in
        the query. Each dictionary holds repository info.
        """
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
        """
        @description: As requested on the assignment, obtains the 5 most
        recent repos matching the query term, sorted.
        @arg results_list: {list} The first page of results, returned by
        GitHub's API.
        @return: {list} A filtered list of results, as required on the assignment.
        """
        results_list = sorted(results_list,
            key=lambda x: x["created_at"],
            reverse=True
        )
        return results_list[:5]
        
        
    @classmethod
    def include_indexes(cls, results_list):
        """
        @description: Includes a 'index' key on each repo's dictionary.
        It will come handy for printing the results' indexes on the HTML template.
        @arg results_list: {list} A list containing dictionaries of repository info.
        @result: {list} The list of dictionaries, after indexing.
        """
        for i, result in enumerate(results_list):
            result["index"] = i+1
        return results_list
        
    
    @classmethod
    def obtain_last_commit_info(cls, commits_url):
        """
        @description: Given a repo's commits url, obtains some of its last commit's info.
        @arg commits_url: {str} A repository's commits url.
        @return: {tuple or None} If the repository has any commits, this function
        returns a tuple of type (sha, commit_message, author_name). Otherwise
        returns None.
        """
        r = requests.get(commits_url, headers=cls.headers)
        if r.status_code == 200:
            commits = json.loads(r.content.decode("utf-8"))
            if len(commits) > 0:
                return(
                    commits[0]["sha"],
                    commits[0]["commit"]["message"],
                    commits[0]["commit"]["author"]["name"]
                    )
        return None
        
        
    @classmethod
    def include_last_commit_info(cls, repo_info):
        """
        @description: Includes the required last commit's info, on a given 
        repository's dictionary.
        @arg repo_info: {dict} A dictionary containing a repository's info.
        @return: {dict} The dictionary after inserting the required last commit's info.
        """
        last_commit_info = cls.obtain_last_commit_info(
            repo_info["commits_url"].replace("{/sha}", ""))
            
        if last_commit_info != None:
            repo_info["sha"], repo_info["message"], repo_info["author"] = last_commit_info
            
        return repo_info
        
        
@click.command()
@click.option('--port', default=9876, help='Port number of the web server')
def run_navigator(port):
    app.run(host="0.0.0.0", port=port)
            

if __name__ == "__main__":
    run_navigator()