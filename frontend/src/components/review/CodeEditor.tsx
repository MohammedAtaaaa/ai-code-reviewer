import Editor from '@monaco-editor/react'
import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileCode } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CodeEditorProps {
  code: string
  language: string
  onChange: (value: string) => void
  onLanguageChange: (lang: string) => void
  theme: 'light' | 'dark'
}

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'php', label: 'PHP' },
]

export function CodeEditor({ code, language, onChange, onLanguageChange, theme }: CodeEditorProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = () => {
        const text = reader.result as string
        onChange(text)
        const ext = file.name.split('.').pop()?.toLowerCase()
        const langMap: Record<string, string> = {
          py: 'python',
          js: 'javascript',
          ts: 'typescript',
          jsx: 'javascript',
          tsx: 'typescript',
          java: 'java',
          go: 'go',
          rs: 'rust',
          cpp: 'cpp',
          c: 'c',
          rb: 'ruby',
          php: 'php',
        }
        if (ext && langMap[ext]) onLanguageChange(langMap[ext])
      }
      reader.readAsText(file)
    },
    [onChange, onLanguageChange],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    noClick: true,
    noKeyboard: true,
    accept: {
      'text/*': ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp', '.c', '.rb', '.php', '.txt'],
    },
  })

  return (
    <div className="space-y-3">
      {/* Language selector */}
      <div className="flex items-center gap-3">
        <FileCode size={16} className="text-muted-foreground" />
        <select
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
          className="rounded-lg border border-input bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring cursor-pointer"
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>
        <span className="text-xs text-muted-foreground">Drag & drop a file or paste code below</span>
      </div>

      {/* Editor with drop zone */}
      <div
        {...getRootProps()}
        className={cn(
          'relative overflow-hidden rounded-xl border border-border transition-all duration-200',
          isDragActive && 'border-primary ring-2 ring-primary/20',
        )}
      >
        <input {...getInputProps()} />
        {isDragActive && (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-primary/5 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-2 text-primary">
              <Upload size={40} />
              <span className="text-sm font-medium">Drop your code file here</span>
            </div>
          </div>
        )}
        <Editor
          height="400px"
          language={language}
          value={code}
          theme={theme === 'dark' ? 'vs-dark' : 'light'}
          onChange={(v) => onChange(v || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
            wordWrap: 'on',
            renderWhitespace: 'selection',
            bracketPairColorization: { enabled: true },
            fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
            fontLigatures: true,
          }}
        />
      </div>
    </div>
  )
}
