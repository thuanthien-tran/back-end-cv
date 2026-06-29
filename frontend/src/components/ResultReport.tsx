import { useState } from 'react';

interface ScoreItem {
  score: number;
  weight: number;
  description: string;
}

interface ResultData {
  compatibility?: {
    overall_score: number;
    level: string;
    recommendation: string;
    message: string;
    confidence: number;
  };
  score_breakdown?: Record<string, ScoreItem>;
  skills_analysis?: {
    matched_skills: string[];
    missing_skills: string[];
    extra_skills: string[];
    skill_match_ratio: number;
  };
  candidate_summary?: {
    summary: string | null;
    strengths: string[];
    weaknesses: string[];
    risk_flags: string[];
  };
  recommendations?: {
    for_recruiter: string[];
    for_candidate: string[];
  };
  interview_questions?: string[];
  alternative_roles?: string[];
  warnings?: string[];
  metadata?: {
    ai_provider: string | null;
    ai_model: string | null;
    processing_time_seconds: number | null;
  };
}

type TabKey = 'overview' | 'skills' | 'recommendations' | 'interview';

function formatLabel(value: string): string {
  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getScoreClass(score: number): string {
  if (score >= 85) return 'excellent';
  if (score >= 70) return 'strong';
  if (score >= 55) return 'medium';
  if (score >= 40) return 'weak';
  return 'bad';
}

function getBarColor(score: number): string {
  if (score >= 85) return '#16a34a';
  if (score >= 70) return '#2563eb';
  if (score >= 55) return '#d97706';
  if (score >= 40) return '#ea580c';
  return '#dc2626';
}

function ScoreBar({ label, score, description }: { label: string; score: number; description?: string }) {
  return (
    <div className="score-bar-row">
      <div className="score-bar-header">
        <span>{label}</span>
        <strong style={{ color: getBarColor(score) }}>{score}%</strong>
      </div>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${Math.min(score, 100)}%`, background: getBarColor(score) }} />
      </div>
      {description && <div className="score-bar-desc">{description}</div>}
    </div>
  );
}

export default function ResultReport({ result }: { result: ResultData | null }) {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  if (!result || !result.compatibility) return null;

  const { compatibility, score_breakdown, skills_analysis, candidate_summary, recommendations, interview_questions, alternative_roles, warnings, metadata } = result;
  const scoreClass = getScoreClass(compatibility.overall_score);

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'skills', label: 'Skills' },
    { key: 'recommendations', label: 'Recommendations' },
    { key: 'interview', label: 'Interview' },
  ];

  return (
    <div className="result-report">
      {/* Warnings Banner */}
      {warnings && warnings.length > 0 && (
        <div className="warnings-banner">
          <div className="warning-icon">⚠️</div>
          <div className="warning-content">
            <strong>Cảnh báo chất lượng dữ liệu:</strong>
            <ul>
              {warnings.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          </div>
        </div>
      )}

      <div className={`score-card ${scoreClass}`}>
        <div className="score-card-content">
          <div className="score-card-label">Overall Compatibility</div>
          <div className="big-score">{compatibility.overall_score}%</div>
          <div className="score-card-level">{compatibility.level}</div>
          <div className="score-card-rec">{compatibility.recommendation}</div>
        </div>
        <div className="score-card-message">{compatibility.message}</div>
      </div>

      <div className="tab-bar">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <>
            {score_breakdown && (
              <div className="report-card">
                <h3>Score Breakdown</h3>
                {Object.entries(score_breakdown).map(([key, item]) => (
                  <ScoreBar key={key} label={formatLabel(key)} score={item.score} description={item.description} />
                ))}
              </div>
            )}

            {candidate_summary && (
              <div className="report-card">
                <h3>Summary</h3>
                {candidate_summary.summary && <p className="summary-text">{candidate_summary.summary}</p>}

                {candidate_summary.strengths.length > 0 && (
                  <>
                    <h4>Strengths</h4>
                    <ul>
                      {candidate_summary.strengths.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </>
                )}

                {candidate_summary.weaknesses.length > 0 && (
                  <>
                    <h4>Weaknesses</h4>
                    <ul>
                      {candidate_summary.weaknesses.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </>
                )}

                {candidate_summary.risk_flags.length > 0 && (
                  <>
                    <h4>Risk Flags</h4>
                    <ul className="risk-list">
                      {candidate_summary.risk_flags.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </>
                )}
              </div>
            )}
          </>
        )}

        {activeTab === 'skills' && skills_analysis && (
          <div className="report-card">
            <h3>Skills Analysis</h3>
            <p className="skill-ratio">
              Skill Match Ratio: <strong style={{ color: getBarColor(skills_analysis.skill_match_ratio) }}>
                {skills_analysis.skill_match_ratio}%
              </strong>
            </p>

            <ScoreBar label="Skill Match" score={skills_analysis.skill_match_ratio} />

            {skills_analysis.matched_skills.length > 0 && (
              <div className="tag-section">
                <h4>Matched Skills</h4>
                <div className="tags">
                  {skills_analysis.matched_skills.map((skill) => (
                    <span className="tag success" key={skill}>&#10003; {skill}</span>
                  ))}
                </div>
              </div>
            )}

            {skills_analysis.missing_skills.length > 0 && (
              <div className="tag-section">
                <h4>Missing Skills</h4>
                <div className="tags">
                  {skills_analysis.missing_skills.map((skill) => (
                    <span className="tag danger" key={skill}>&#9888; {skill}</span>
                  ))}
                </div>
              </div>
            )}

            {skills_analysis.extra_skills.length > 0 && (
              <div className="tag-section">
                <h4>Extra Skills</h4>
                <div className="tags">
                  {skills_analysis.extra_skills.map((skill) => (
                    <span className="tag neutral" key={skill}>+ {skill}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'recommendations' && recommendations && (
          <>
            <div className="report-card">
              <h3>For Recruiter</h3>
              <ul>
                {recommendations.for_recruiter.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>

            <div className="report-card">
              <h3>For Candidate</h3>
              <ul>
                {recommendations.for_candidate.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>

            {alternative_roles && alternative_roles.length > 0 && (
              <div className="report-card">
                <h3>Alternative Suitable Roles</h3>
                <p className="alternative-roles-desc">Dựa trên hồ sơ ứng viên, các vị trí sau có thể phù hợp hơn:</p>
                <div className="tags">
                  {alternative_roles.map((role, i) => (
                    <span className="tag success" key={i}>&#10148; {role}</span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === 'interview' && interview_questions && interview_questions.length > 0 && (
          <div className="report-card">
            <h3>Interview Questions</h3>
            <ol className="interview-list">
              {interview_questions.map((q, i) => <li key={i}>{q}</li>)}
            </ol>
          </div>
        )}
      </div>

      {metadata && (
        <div className="report-meta">
          AI: {metadata.ai_provider || 'N/A'} / {metadata.ai_model || 'N/A'} | Processing: {metadata.processing_time_seconds?.toFixed(2) || 'N/A'}s
        </div>
      )}
    </div>
  );
}
