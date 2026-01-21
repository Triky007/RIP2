import React, { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import {
    Upload,
    FileText,
    Download,
    Settings,
    Image as ImageIcon,
    Loader2,
    CheckCircle2,
    AlertCircle,
    Eye
} from 'lucide-react';

const FORMATS = [
    { id: 'tiff1b', name: 'TIFF 1-bit', description: 'Binary Monochrome' },
    { id: 'bmp2b', name: 'BMP 2-bit', description: '4 Colors Palette' },
    { id: 'bmp4b', name: 'BMP 4-bit', description: '16 Colors Palette' },
    { id: 'bmp8b', name: 'BMP 8-bit', description: '256 Colors Grayscale' },
];

function App() {
    const [file, setFile] = useState(null);
    const [format, setFormat] = useState('tiff1b');
    const [dpi, setDpi] = useState(300);
    const [noise, setNoise] = useState(0);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const onDrop = (acceptedFiles) => {
        setFile(acceptedFiles[0]);
        setError(null);
        setResult(null);
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        multiple: false
    });

    const handleProcess = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('format', format);
        formData.append('dpi', dpi);
        formData.append('noise', noise / 100); // 0-100 to 0.0-1.0

        try {
            const response = await axios.post('/api/process', formData);
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred during processing');
        } finally {
            setLoading(false);
        }
    };

    const downloadResult = () => {
        if (!result) return;
        window.open(`/api/download/${result.id}`, '_blank');
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 p-8 flex flex-col items-center">
            <header className="mb-12 text-center">
                <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-primary-400 to-indigo-400 bg-clip-text text-transparent mb-4">
                    Stochastic RIP
                </h1>
                <p className="text-slate-400 text-lg max-w-2xl">
                    High-performance PDF rasterizer with Floyd-Steinberg error diffusion.
                    Vector to screened bitmap in seconds.
                </p>
            </header>

            <main className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Configuration Panel */}
                <section className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 backdrop-blur-xl shadow-2xl">
                    <div className="flex items-center gap-3 mb-8">
                        <Settings className="w-6 h-6 text-primary-400" />
                        <h2 className="text-2xl font-semibold">Processing Settings</h2>
                    </div>

                    <div className="space-y-8">
                        {/* Format Selection */}
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-4">Output Format</label>
                            <div className="grid grid-cols-2 gap-4">
                                {FORMATS.map((f) => (
                                    <button
                                        key={f.id}
                                        onClick={() => setFormat(f.id)}
                                        className={`flex flex-col items-start p-4 rounded-2xl border transition-all duration-200 text-left ${format === f.id
                                            ? 'bg-primary-500/10 border-primary-500/50 ring-1 ring-primary-500/50'
                                            : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                                            }`}
                                    >
                                        <span className={`font-semibold ${format === f.id ? 'text-primary-300' : 'text-slate-200'}`}>
                                            {f.name}
                                        </span>
                                        <span className="text-xs text-slate-500 mt-1">{f.description}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* DPI Settings */}
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <label className="text-sm font-medium text-slate-400">Resolution (DPI)</label>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => setDpi(300)}
                                        className={`text-xs px-2 py-1 rounded ${dpi === 300 ? 'bg-primary-500 text-white' : 'bg-slate-800 text-slate-400'}`}
                                    >300</button>
                                    <button
                                        onClick={() => setDpi(600)}
                                        className={`text-xs px-2 py-1 rounded ${dpi === 600 ? 'bg-primary-500 text-white' : 'bg-slate-800 text-slate-400'}`}
                                    >600</button>
                                    <button
                                        onClick={() => setDpi("1200x600")}
                                        className={`text-xs px-2 py-1 rounded ${dpi === "1200x600" ? 'bg-primary-500 text-white' : 'bg-slate-800 text-slate-400'}`}
                                    >1200x600</button>
                                </div>
                            </div>

                            <div className="flex items-center bg-slate-800 rounded-lg border border-slate-700 focus-within:border-primary-500 transition-colors">
                                <input
                                    type="text"
                                    value={dpi}
                                    onChange={(e) => setDpi(e.target.value)}
                                    className="w-full bg-transparent px-4 py-2 text-slate-200 outline-none font-mono placeholder-slate-600"
                                    placeholder="e.g. 300 or 1200x600"
                                />
                            </div>
                            <p className="text-xs text-slate-500 mt-2">
                                Format: <span className="font-mono text-slate-400">Value</span> (symmetric) or <span className="font-mono text-slate-400">XxY</span> (asymmetric)
                            </p>
                        </div>

                        {/* Noise Settings */}
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <label className="text-sm font-medium text-slate-400 flex items-center gap-2">
                                    Noise Injection
                                    <span className="text-xs font-normal text-slate-600 bg-slate-800 px-2 py-0.5 rounded-full">Reduces Patterns</span>
                                </label>
                                <span className="text-indigo-400 font-mono font-bold font-lg">{noise}%</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="50"
                                step="1"
                                value={noise}
                                onChange={(e) => setNoise(parseInt(e.target.value))}
                                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500 hover:accent-indigo-400 transition-all"
                            />
                        </div>

                        {/* Upload Area */}
                        <div
                            {...getRootProps()}
                            className={`relative border-2 border-dashed rounded-3xl p-10 transition-all duration-300 flex flex-col items-center justify-center cursor-pointer ${isDragActive
                                ? 'border-primary-500 bg-primary-500/5 scale-[0.98]'
                                : 'border-slate-700 hover:border-slate-500 bg-slate-800/30'
                                }`}
                        >
                            <input {...getInputProps()} />
                            <div className="bg-slate-800 p-4 rounded-full mb-4 group-hover:bg-slate-700 transition-colors">
                                <Upload className={`w-8 h-8 ${isDragActive ? 'text-primary-400 animate-bounce' : 'text-slate-400'}`} />
                            </div>

                            {file ? (
                                <div className="text-center">
                                    <p className="text-slate-200 font-medium truncate max-w-[200px]">{file.name}</p>
                                    <p className="text-slate-500 text-xs mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                            ) : (
                                <div className="text-center">
                                    <p className="text-slate-300 font-medium">Drop your PDF here</p>
                                    <p className="text-slate-500 text-sm mt-1">or click to browse</p>
                                </div>
                            )}
                        </div>

                        {/* Process Button */}
                        <button
                            onClick={handleProcess}
                            disabled={!file || loading}
                            className={`w-full py-4 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-3 shadow-xl ${!file || loading
                                ? 'bg-slate-800 text-slate-600 cursor-not-allowed'
                                : 'bg-primary-500 hover:bg-primary-600 text-white hover:scale-[1.02] active:scale-[0.98]'
                                }`}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                    Rasterizing...
                                </>
                            ) : (
                                <>
                                    <CheckCircle2 className="w-6 h-6" />
                                    Start Process
                                </>
                            )}
                        </button>

                        {error && (
                            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/50 rounded-2xl text-red-400 text-sm animate-in fade-in slide-in-from-top-2">
                                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                <p>{error}</p>
                            </div>
                        )}
                    </div>
                </section>

                {/* Results Panel */}
                <section className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 backdrop-blur-xl shadow-2xl flex flex-col h-full min-h-[600px]">
                    <div className="flex items-center gap-3 mb-8">
                        <ImageIcon className="w-6 h-6 text-indigo-400" />
                        <h2 className="text-2xl font-semibold">Preview & Output</h2>
                    </div>

                    <div className="flex-grow flex flex-col justify-center items-center border border-slate-800 rounded-2xl bg-slate-950/50 overflow-hidden relative group">
                        {result ? (
                            <div className="w-full h-full flex flex-col p-4">
                                <div className="flex-grow relative overflow-auto rounded-xl border border-slate-800 bg-checkerboard">
                                    <img
                                        src={`/api${result.preview_url}`}
                                        alt="Process Preview"
                                        className="max-w-none w-full object-contain shadow-2xl"
                                    />
                                </div>

                                <div className="mt-6 flex flex-col sm:flex-row gap-4">
                                    <button
                                        onClick={downloadResult}
                                        className="flex-grow flex items-center justify-center gap-2 bg-indigo-500 hover:bg-indigo-600 text-white py-3 rounded-xl font-bold transition-all"
                                    >
                                        <Download className="w-5 h-5" />
                                        Download {result.filename.split('.').pop().toUpperCase()}
                                    </button>
                                    <a
                                        href={`/api${result.preview_url}`}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="flex items-center justify-center p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all border border-slate-700"
                                        title="View Raw Preview"
                                    >
                                        <Eye className="w-5 h-5" />
                                    </a>
                                </div>

                                <div className="mt-4 flex items-center justify-center gap-6 text-xs text-slate-500 font-mono bg-slate-800/30 p-2 rounded-lg">
                                    <span className="flex items-center gap-1"><FileText className="w-3 h-3" /> {result.filename}</span>
                                    <span className="flex items-center gap-1 uppercase font-bold text-indigo-400">{format}</span>
                                    <span className="flex items-center gap-1 font-bold">{dpi} DPI</span>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center p-8">
                                {loading ? (
                                    <div className="space-y-4">
                                        <Loader2 className="w-12 h-12 text-primary-400 animate-spin mx-auto mb-4" />
                                        <p className="text-slate-400 animate-pulse font-medium">Computing stochastic matrix...</p>
                                        <p className="text-slate-600 text-xs italic">Processing large PDFs may take a few seconds</p>
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center opacity-40">
                                        <div className="w-16 h-16 bg-slate-800 rounded-2xl flex items-center justify-center mb-4">
                                            <ImageIcon className="w-8 h-8 text-slate-400" />
                                        </div>
                                        <p className="text-lg font-medium">Ready for input</p>
                                        <p className="text-sm mt-2">Processed results will appear here</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="mt-8">
                        <h3 className="text-xs font-bold text-slate-600 uppercase tracking-widest mb-4">How it works</h3>
                        <div className="grid grid-cols-3 gap-4">
                            <div className="p-3 bg-slate-800/30 rounded-xl border border-slate-800/50">
                                <p className="text-[10px] font-bold text-indigo-400 uppercase mb-1">Step 1</p>
                                <p className="text-[11px] text-slate-500 leading-relaxed font-medium">Ghostscript interprets vector paths and converts to high-res grayscale.</p>
                            </div>
                            <div className="p-3 bg-slate-800/30 rounded-xl border border-slate-800/50">
                                <p className="text-[10px] font-bold text-primary-400 uppercase mb-1">Step 2</p>
                                <p className="text-[11px] text-slate-500 leading-relaxed font-medium">Floyd-Steinberg algorithm diffuses quantization errors stochastically.</p>
                            </div>
                            <div className="p-3 bg-slate-800/30 rounded-xl border border-slate-800/50">
                                <p className="text-[10px] font-bold text-emerald-400 uppercase mb-1">Step 3</p>
                                <p className="text-[11px] text-slate-500 leading-relaxed font-medium">The resulting bitmap is packed into the selected bit-depth container.</p>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="mt-auto pt-16 pb-8 text-slate-600 text-sm">
                <p>&copy; 2024 Stochastic RIP Engine • Powered by Ghostscript & FastAPI</p>
            </footer>

            <style>{`
        .bg-checkerboard {
          background-image: 
            linear-gradient(45deg, #0f172a 25%, transparent 25%), 
            linear-gradient(-45deg, #0f172a 25%, transparent 25%), 
            linear-gradient(45deg, transparent 75%, #0f172a 75%), 
            linear-gradient(-45deg, transparent 75%, #0f172a 75%);
          background-size: 20px 20px;
          background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
          background-color: #020617;
        }
      `}</style>
        </div>
    );
}

export default App;
