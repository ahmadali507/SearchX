{/*import React from 'react';

interface ResultsProps {
  results: string[];
}

const Results: React.FC<ResultsProps> = ({ results }) => {
  return (
    <div className="mt-10 p-6 bg-white shadow-md rounded-lg">
      {results.length > 0 ? (
        <ul className="space-y-4">
          {results.map((result, index) => (
            <li key={index} className="text-gray-700 border-b pb-2 hover:text-indigo-500 transition-all">
              {result}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500 text-center">No results found. Try searching for something else!</p>
      )}
    </div>
  );
};

export default Results;
*/}

import React from 'react';

interface ResultsProps {
  results: string[];
}

const Results: React.FC<ResultsProps> = ({ results }) => {
  return (
    <div className="mt-10 p-6 bg-white shadow-md rounded-lg">
      {results.length > 0 ? (
        <ul className="space-y-4">
          {results.map((result, index) => (
            <li key={index} className="text-blue-800 border-b pb-2 hover:text-blue-500 transition-all">
              {result}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-blue-500 text-center">No results found. Try searching for something else!</p>
      )}
    </div>
  );
};

export default Results;
