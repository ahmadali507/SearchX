'use client'

import { useState } from 'react'
import { searchRepositories } from '../app/actions'
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Star, GitFork, ExternalLink, Search, Code, FileCode, Folder, Calendar, Lock, Unlock, Tag, Eye, AlertCircle } from 'lucide-react'

export default function SearchEngine() {
  const [query, setQuery] = useState<string | undefined>('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [queryTime, setQueryTime] = useState<number | null>(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setQueryTime(null) // Reset the query time
    try {
      const startTime = performance.now()
      const data = await searchRepositories(query)
      const endTime = performance.now()
      setQueryTime(Math.round(endTime - startTime)) // Calculate elapsed time in ms
      setResults(data)
    } catch (err) {
      setError('An error occurred while searching. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-4xl">
      <form onSubmit={handleSearch} className="flex gap-2 mb-2">
        <div className="relative flex-grow">
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search GitHub repositories..."
            className="pl-10 pr-4 py-3 w-full bg-white bg-opacity-80 backdrop-blur-sm text-blue-900 placeholder-blue-400 border-blue-300 focus:border-blue-500 focus:ring-blue-500 rounded-full shadow-lg"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-400" />
          {queryTime !== null && (
            <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">
              {queryTime} ms
            </span>
          )}
        </div>
        <Button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-6 py-3 shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105">
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </form>

      {error && (
        <div className="flex items-center space-x-2 text-red-500 mb-4 bg-red-100 p-3 rounded-lg">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      <div key={Math.random()} className="space-y-6">
        {results.map((repo) => (
          <Card key={repo.id} className="bg-white bg-opacity-80 backdrop-blur-sm border-blue-200 shadow-lg hover:shadow-xl transition-all duration-300 ease-in-out transform hover:scale-102 rounded-xl overflow-hidden">
            <CardHeader className="flex flex-row items-center space-x-4 pb-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white">
              <div className="bg-white p-2 rounded-full">
                <Folder className="w-6 h-6 text-blue-600" />
              </div>
              <CardTitle className="text-xl font-semibold">
                <a href={repo.url} target="_blank" rel="noopener noreferrer" className="hover:underline flex items-center gap-2">
                  {repo.name}
                  <ExternalLink size={16} className="text-blue-200" />
                </a>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <p className="text-blue-800 mb-4">Description: {repo?.description}</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-blue-700">
                <div className="flex items-center gap-2">
                  <Star size={16} className="text-yellow-500" />  
                  <span>{repo.stars} stars</span>
                </div>
                <div className="flex items-center gap-2">
                  <GitFork size={16} className="text-green-500" />
                  <span>{repo.forks} forks</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileCode size={16} className="text-purple-500" />
                  <span>{repo.language || 'N/A'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Eye size={16} className="text-blue-500" />
                  <span>{repo.watchers} watchers</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar size={16} className="text-red-500" />
                  <span>Updated: {new Date().toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  {repo.license ? (
                    <>
                      <Lock size={16} className="text-green-500" />
                      <span>{repo.license.spdx_id}</span>
                    </>
                  ) : (
                    <>
                      <Unlock size={16} className="text-yellow-500" />
                      <span>No license</span>
                    </>
                  )}
                </div>
              </div>
              {repo.topics && repo.topics.length > 0 && (
                <div className="mt-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Tag size={16} className="text-blue-500" />
                    <span className="font-semibold text-blue-700">Topics:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {repo.topics.map((topic) => (
                      <span key={topic} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {results.length === 0 && !loading && query && (
        <div className="text-center py-12 bg-white bg-opacity-80 backdrop-blur-sm rounded-xl shadow-lg">
          <Code className="w-20 h-20 text-blue-400 mx-auto mb-4" />
          <p className="text-blue-600 text-xl">No results found. Try a different search query.</p>
        </div>
      )}
    </div>
  )
}
