import { useState, useRef } from 'react';
import ResultReport from './components/ResultReport';

const API_BASE = '/api';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiResult = any;

type LoadingState = {
  register: boolean;
  login: boolean;
  createJob: boolean;
  uploadCv: boolean;
  uploadJd: boolean;
  enqueue: boolean;
  checkStatus: boolean;
  getResult: boolean;
};

function App() {
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('Password123');
  const [accessToken, setAccessToken] = useState('');
  const [refreshToken, setRefreshToken] = useState('');
  const [jobId, setJobId] = useState('');
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [cvUploaded, setCvUploaded] = useState(false);
  const [jdUploaded, setJdUploaded] = useState(false);
  const [jobStatus, setJobStatus] = useState('');
  const [result, setResult] = useState<ApiResult>(null);
  const [message, setMessage] = useState('');
  const [showDebug, setShowDebug] = useState(false);
  const [loading, setLoading] = useState<LoadingState>({
    register: false,
    login: false,
    createJob: false,
    uploadCv: false,
    uploadJd: false,
    enqueue: false,
    checkStatus: false,
    getResult: false,
  });

  const cvInputRef = useRef<HTMLInputElement>(null);
  const jdInputRef = useRef<HTMLInputElement>(null);

  function authHeaders() {
    return { Authorization: `Bearer ${accessToken}` };
  }

  async function handleJson(res: Response) {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || 'Request failed');
    }
    return data;
  }

  function setLoadingKey(key: keyof LoadingState, val: boolean) {
    setLoading((prev) => ({ ...prev, [key]: val }));
  }

  function getCurrentStep(): number {
    if (result?.compatibility) return 4;
    if (jobStatus === 'queued' || jobStatus === 'processing' || jobStatus === 'completed') return 3;
    if (cvUploaded || jdUploaded) return 2;
    if (accessToken) return 1;
    return 0;
  }

  async function register() {
    setLoadingKey('register', true);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: 'Test User' }),
      });
      const data = await handleJson(res);
      setMessage(`Register OK: ${data.email}`);
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoadingKey('register', false);
    }
  }

  async function login() {
    setLoadingKey('login', true);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await handleJson(res);
      setAccessToken(data.access_token);
      setRefreshToken(data.refresh_token || '');
      setMessage('Login successful');
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoadingKey('login', false);
    }
  }

  async function createJob() {
    setLoadingKey('createJob', true);
    try {
      const res = await fetch(`${API_BASE}/jobs`, {
        method: 'POST',
        headers: authHeaders(),
      });
      const data = await handleJson(res);
      setJobId(data.job_id);
      setJobStatus(data.status);
      setCvUploaded(false);
      setJdUploaded(false);
      setResult(null);
      setMessage('Job created — upload CV and JD');
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoadingKey('createJob', false);
    }
  }

  async function uploadFile(type: 'cv' | 'jd') {
    const key = type === 'cv' ? 'uploadCv' : 'uploadJd';
    setLoadingKey(key, true);
    try {
      const file = type === 'cv' ? cvFile : jdFile;
      if (!file) throw new Error(`Choose ${type.toUpperCase()} file first`);
      if (!jobId) throw new Error('Create job first');

      const formData = new FormData();
      formData.append('job_id', jobId);
      formData.append('file_type', type);
      formData.append('file', file);

      const res = await fetch(`${API_BASE}/uploads`, {
        method: 'POST',
        headers: authHeaders(),
        body: formData,
      });
      await handleJson(res);
      if (type === 'cv') setCvUploaded(true);
      else setJdUploaded(true);
      setMessage(`${type.toUpperCase()} uploaded successfully`);
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoadingKey(key, false);
    }
  }

  async function enqueueJob() {
    setLoadingKey('enqueue', true);
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/enqueue`, {
        method: 'POST',
        headers: authHeaders(),
      });
      const data = await handleJson(res);
      setJobStatus(data.status);
      setMessage('Job enqueued — analyzing...');
      pollStatus();
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoadingKey('enqueue', false);
    }
  }

  async function pollStatus() {
    const poll = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
          headers: authHeaders(),
        });
        const data = await handleJson(res);
        setJobStatus(data.status);
        if (data.status === 'completed') {
          clearInterval(poll);
          setMessage('Analysis completed — loading result...');
          await loadResult();
        } else if (data.status === 'failed') {
          clearInterval(poll);
          setMessage(`Analysis failed: ${data.error_message || 'Unknown error'}`);
        }
      } catch {
        clearInterval(poll);
      }
    }, 2000);
  }

  async function loadResult() {
    setLoadingKey('getResult', true);
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/result`, {
        headers: authHeaders(),
      });
      const data = await handleJson(res);
      setResult(data);
      setMessage('');
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoadingKey('getResult', false);
    }
  }

  async function checkStatus() {
    setLoadingKey('checkStatus', true);
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
        headers: authHeaders(),
      });
      const data = await handleJson(res);
      setJobStatus(data.status);
      if (data.status === 'completed') {
        await loadResult();
      }
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoadingKey('checkStatus', false);
    }
  }

  function handleDrop(type: 'cv' | 'jd', e: React.DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      if (type === 'cv') setCvFile(file);
      else setJdFile(file);
    }
  }

  const step = getCurrentStep();

  return (
    <div className="container">
      <header className="app-header">
        <h1>ResumeFit AI</h1>
        <p className="subtitle">Analyze candidate compatibility, skill gaps, and interview readiness.</p>
      </header>

      <div className="steps">
        <div className={`step ${step >= 1 ? 'active' : ''} ${step === 0 ? 'current' : ''}`}>1. Login</div>
        <div className={`step ${step >= 2 ? 'active' : ''} ${step === 1 ? 'current' : ''}`}>2. Upload</div>
        <div className={`step ${step >= 3 ? 'active' : ''} ${step === 2 ? 'current' : ''}`}>3. Analyze</div>
        <div className={`step ${step >= 4 ? 'active' : ''} ${step === 3 ? 'current' : ''}`}>4. Result</div>
      </div>

      {message && (
        <div className="message-bar">
          <span>{message}</span>
          <button className="message-close" onClick={() => setMessage('')} aria-label="Close">&times;</button>
        </div>
      )}

      {!accessToken && (
        <div className="card">
          <h2>Login or Register</h2>
          <div className="row">
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <button onClick={login} disabled={loading.login}>
              {loading.login ? 'Logging in...' : 'Login'}
            </button>
            <button className="secondary" onClick={register} disabled={loading.register}>
              {loading.register ? 'Registering...' : 'Register'}
            </button>
          </div>
        </div>
      )}

      {accessToken && !result?.compatibility && (
        <>
          <div className="status-bar">
            <span>Logged in as <strong>{email}</strong></span>
            <span className="badge badge-green">Session Active</span>
            {jobId && <span>Job: <code>{jobId.slice(0, 8)}...</code> <span className={`badge badge-${jobStatus === 'completed' ? 'green' : jobStatus === 'failed' ? 'red' : 'default'}`}>{jobStatus || 'created'}</span></span>}
          </div>

          {!jobId && (
            <div className="card">
              <h2>Start New Analysis</h2>
              <p>Create a new job, then upload your CV and Job Description.</p>
              <button onClick={createJob} disabled={loading.createJob}>
                {loading.createJob ? 'Creating...' : 'Create New Job'}
              </button>
            </div>
          )}

          {jobId && jobStatus !== 'completed' && (
            <div className="card">
              <h2>Upload Documents</h2>
              <p>PDF or DOCX only, max 10MB.</p>

              <div className="upload-grid">
                <div
                  className={`upload-box ${cvUploaded ? 'uploaded' : ''}`}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => handleDrop('cv', e)}
                  onClick={() => cvInputRef.current?.click()}
                >
                  <input
                    ref={cvInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    style={{ display: 'none' }}
                    onChange={(e) => setCvFile(e.target.files?.[0] || null)}
                  />
                  <div className="upload-icon">{cvUploaded ? '✓' : '📄'}</div>
                  <div className="upload-title">{cvUploaded ? 'CV Uploaded' : 'Upload CV'}</div>
                  <div className="upload-note">
                    {cvFile ? cvFile.name : 'Drag & drop or click to select'}
                  </div>
                  {cvFile && !cvUploaded && (
                    <button
                      className="upload-btn"
                      disabled={loading.uploadCv}
                      onClick={(e) => { e.stopPropagation(); uploadFile('cv'); }}
                    >
                      {loading.uploadCv ? 'Uploading...' : 'Upload'}
                    </button>
                  )}
                </div>

                <div
                  className={`upload-box ${jdUploaded ? 'uploaded' : ''}`}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => handleDrop('jd', e)}
                  onClick={() => jdInputRef.current?.click()}
                >
                  <input
                    ref={jdInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    style={{ display: 'none' }}
                    onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                  />
                  <div className="upload-icon">{jdUploaded ? '✓' : '📋'}</div>
                  <div className="upload-title">{jdUploaded ? 'JD Uploaded' : 'Upload Job Description'}</div>
                  <div className="upload-note">
                    {jdFile ? jdFile.name : 'Drag & drop or click to select'}
                  </div>
                  {jdFile && !jdUploaded && (
                    <button
                      className="upload-btn"
                      disabled={loading.uploadJd}
                      onClick={(e) => { e.stopPropagation(); uploadFile('jd'); }}
                    >
                      {loading.uploadJd ? 'Uploading...' : 'Upload'}
                    </button>
                  )}
                </div>
              </div>

              {cvUploaded && jdUploaded && jobStatus !== 'queued' && jobStatus !== 'processing' && (
                <div style={{ marginTop: 20, textAlign: 'center' }}>
                  <button className="btn-primary-lg" onClick={enqueueJob} disabled={loading.enqueue}>
                    {loading.enqueue ? 'Submitting...' : 'Analyze CV vs JD'}
                  </button>
                </div>
              )}

              {(jobStatus === 'queued' || jobStatus === 'processing') && (
                <div className="analyzing-state">
                  <div className="spinner" />
                  <span>Analyzing... please wait</span>
                  <button className="secondary" onClick={checkStatus} disabled={loading.checkStatus}>
                    {loading.checkStatus ? 'Checking...' : 'Refresh'}
                  </button>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {result?.compatibility && (
        <>
          <ResultReport result={result} />

          <div style={{ textAlign: 'center', margin: '24px 0' }}>
            <button className="secondary" onClick={() => window.print()}>Print Report</button>
            <button className="secondary" style={{ marginLeft: 12 }} onClick={() => {
              const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `report-${jobId.slice(0, 8)}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}>Download JSON</button>
            <button style={{ marginLeft: 12 }} onClick={() => {
              setResult(null);
              setJobId('');
              setJobStatus('');
              setCvFile(null);
              setJdFile(null);
              setCvUploaded(false);
              setJdUploaded(false);
            }}>New Analysis</button>
          </div>
        </>
      )}

      <div className="debug-section">
        <button className="debug-toggle" onClick={() => setShowDebug(!showDebug)}>
          {showDebug ? 'Hide' : 'Show'} Developer Debug
        </button>
        {showDebug && (
          <div className="card debug-card">
            <p>Access Token: <code>{accessToken ? accessToken.slice(0, 20) + '...' : 'None'}</code></p>
            <p>Refresh Token: <code>{refreshToken ? 'OK' : 'None'}</code></p>
            <p>Job ID: <code>{jobId || 'None'}</code></p>
            <p>Status: <code>{jobStatus || 'None'}</code></p>
            <h4>Raw Result</h4>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>

      <footer className="app-footer">
        <a href="/docs" target="_blank">API Docs</a>
      </footer>
    </div>
  );
}

export default App;
