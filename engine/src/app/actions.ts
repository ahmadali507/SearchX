'use server'

import { Octokit } from "@octokit/rest";

const octokit = new Octokit({
  auth: process.env.GITHUB_API_TOKEN
});

export async function searchRepositories(query: string) {
  try {
    const response = await octokit.search.repos({
      q: query,
      sort: "stars",
      order: "desc",
      per_page: 10,
    });
    
    const detailedResults = await Promise.all(
      response.data.items.map(async (repo) => {
        const { data: repoDetails } = await octokit.repos.get({
          owner: repo.owner.login,
          repo: repo.name,
        });
        
        return {
          ...repo,
          topics: repoDetails.topics,
          license: repoDetails.license,
          updated_at: repoDetails.updated_at,
          watchers_count: repoDetails.watchers_count,
        };
      })
    );
    
    return detailedResults;
  } catch (error) {
    console.error("Error searching repositories:", error);
    throw new Error("Failed to search repositories");
  }
}

