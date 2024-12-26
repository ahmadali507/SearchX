'use server'

import { Octokit } from "@octokit/rest";
import axios from "axios";

const octokit = new Octokit({
  auth: process.env.GITHUB_API_TOKEN
});

export async function searchRepositories(query: string) {
  try {

    console.log('entered the search part')
    // const response = await octokit.search.repos({
    //   q: query,
    //   sort: "stars",
    //   order: "desc",
    //   per_page: 10,
    // });
    
    const reqData = {query :query}; 

    console.log(reqData)
    const response = await axios.post('http://localhost:5000/search', reqData , {
      headers : {
        "Content-Type" : "application/json",
      }
    }); 

    console.log(response.data.results[0].description);
    const detailedResults = await Promise.all(
      response.data.results.map(async (repo) => {
        const {name, description, forks, stars, watchers, url} = repo;
        
        return {
          name : name, 
          description : description, 
          forks : forks, 
          stars : stars, 
          watchers : watchers,
          url : url,
        };
      })
    );
    
    return detailedResults;
  } catch (error) {
    console.error("Error searching repositories:", error);
    throw new Error("Failed to search repositories");
  }
}

