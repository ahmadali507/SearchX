import SearchEngine from '../components/search-engine'
import { Code, Database, GitBranch, Terminal, Cloud, Cpu, Globe, Layers } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-100 to-blue-200 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="flex items-center mb-8 space-x-4">
        <Code className="w-12 h-12 text-blue-600" />
        <h1 className="text-4xl font-bold text-blue-800">GitHub Repo Explorer - SearchX</h1>
        <GitBranch className="w-12 h-12 text-blue-600" />
      </div>
      <SearchEngine />
      <div className="absolute top-4 left-4 text-blue-400">
        <Terminal className="w-8 h-8" />
      </div>
      <div className="absolute bottom-4 right-4 text-blue-400">
        <Database className="w-8 h-8" />
      </div>
      <div className="absolute top-1/4 left-1/4 text-blue-300 opacity-20">
        <Cloud className="w-24 h-24" />
      </div>
      <div className="absolute bottom-1/4 right-1/4 text-blue-300 opacity-20">
        <Cpu className="w-24 h-24" />
      </div>
      <div className="absolute top-3/4 left-1/3 text-blue-300 opacity-20">
        <Globe className="w-20 h-20" />
      </div>
      <div className="absolute bottom-2/3 right-1/3 text-blue-300 opacity-20">
        <Layers className="w-20 h-20" />
      </div>
    </main>
  )
}

