{/*import React, { useState } from 'react';
import InputField from './InputField';
import SearchButton from './SearchButton';

interface SearchBarProps {
  onSearch: (query: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState<string>('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSearch} className="flex justify-center mt-8">
      <InputField value={query} onChange={(e) => setQuery(e.target.value)} />
      <SearchButton />
    </form>
  );
};

export default SearchBar;
*/}

import React, { useState } from 'react';
import InputField from './InputField';
import SearchButton from './SearchButton';

interface SearchBarProps {
  onSearch: (query: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState<string>('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSearch} className="flex justify-center mt-8">
      <InputField value={query} onChange={(e) => setQuery(e.target.value)} />
      <SearchButton />
    </form>
  );
};

export default SearchBar;
