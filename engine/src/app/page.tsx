"use client";

{/*

import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Results from './components/Results';
import { useState } from 'react';

export default function Home() {
  const [results, setResults] = useState<string[]>([]);

  const handleSearch = (query: string) => {
    // Simulate a search operation (replace with real API call later)
    const mockResults = [
      `Result 1 for "${query}"`,
      `Result 2 for "${query}"`,
      `Result 3 for "${query}"`
    ];
    setResults(mockResults);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 font-sans">
      <Header />
      <SearchBar onSearch={handleSearch} />
      <Results results={results} />
    </div>
  );
}
*/}

import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Results from './components/Results';
import { useState } from 'react';

export default function Home() {
  const [results, setResults] = useState<string[]>([]);

  const handleSearch = (query: string) => {
    // Simulate a search operation (replace with real API call later)
    const mockResults = [
      `"${query}"`,
      `"${query}"`,
      `"${query}"`
    ];
    setResults(mockResults);
  };

  return (
    <div className="min-h-screen bg-blue-50 text-blue-800 font-sans">
      <Header />
      <SearchBar onSearch={handleSearch} />
      <Results results={results} />
    </div>
  );
}
