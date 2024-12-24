{/*import React from 'react';

interface InputFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const InputField: React.FC<InputFieldProps> = ({ value, onChange }) => {
  return (
    <input
      type="text"
      placeholder="Search..."
      value={value}
      onChange={onChange}
      className="border-2 border-gray-300 p-4 rounded-lg w-80 text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300 placeholder:text-gray-400 transition-all"
    />
  );
};

export default InputField;
*/}

import React from 'react';

interface InputFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const InputField: React.FC<InputFieldProps> = ({ value, onChange }) => {
  return (
    <input
      type="text"
      placeholder="Search..."
      value={value}
      onChange={onChange}
      className="border-2 border-blue-300 p-4 rounded-lg w-80 text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder:text-blue-400 transition-all"
    />
  );
};

export default InputField;
