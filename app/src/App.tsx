import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Activity,
  ArrowDown,
  ArrowRight,
  ArrowUp,
  BarChart3,
  ChevronRight,
  CircleDot,
  ClipboardList,
  Download,
  Gauge,
  Goal,
  LayoutDashboard,
  Search,
  Shield,
  Star,
  Target,
  TrendingUp,
  Users,
  X,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { HalfRink, NetFront } from "./components/Rinks";
import type {
  Confidence,
  GmPlayer,
  PrescoutData,
  Stat,
  SummaryData,
} from "./types/prescout";

type Mode = "coach" | "gm";
type CoachPage = "summary" | "specialTeams" | "faceoffs" | "goalie" | "gameState" | "playerTargets";
type GmPage = "gmSummary" | "players";
type Page = CoachPage | GmPage;

const coachNav: Array<{ id: CoachPage; label: string; icon: typeof Activity }> = [
  { id: "summary", label: "Game Summary", icon: LayoutDashboard },
  { id: "specialTeams", label: "Special Teams", icon: Shield },
  { id: "faceoffs", label: "Faceoffs", icon: CircleDot },
  { id: "goalie", label: "Goalie", icon: Goal },
  { id: "gameState", label: "Game State", icon: Activity },
  { id: "playerTargets", label: "Player Targets", icon: Target },
];

const gmNav: Array<{ id: GmPage; label: string; icon: typeof Activity }> = [
  { id: "gmSummary", label: "GM Summary", icon: BarChart3 },
  { id: "players", label: "Player Evaluation", icon: Users },
];

function Button({
  children,
  className = "",
  onClick,
  ariaLabel,
}: {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  ariaLabel?: string;
}) {
  return (
    <button type="button" className={className} onClick={onClick} aria-label={ariaLabel}>
      {children}
    </button>
  );
}

function TextInput({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}) {
  return (
    <input
      value={value}
      onChange={(event) => onChange(event.target.value)}
      placeholder={placeholder}
      className="search-input"
    />
  );
}

function ConfidenceBadge({ confidence }: { confidence: Confidence }) {
  return <span className={`confidence confidence-${confidence}`}>{confidence}</span>;
}

function StatMeta<T>({ stat }: { stat: Stat<T> }) {
  return (
    <span className="stat-meta">
      <span>n={stat.sampleSize}</span>
      <ConfidenceBadge confidence={stat.confidence} />
      {stat.isEstimate && <span className="estimate">Estimate</span>}
    </span>
  );
}

function StatValue<T>({
  stat,
  className = "",
  format,
}: {
  stat: Stat<T>;
  className?: string;
  format?: (value: T) => ReactNode;
}) {
  return (
    <span className={`stat-value ${className}`}>
      <span>{format ? format(stat.value) : String(stat.value)}</span>
      <StatMeta stat={stat} />
    </span>
  );
}

function Card({
  children,
  className = "",
  title,
  eyebrow,
  action,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
}) {
  return (
    <section className={`card ${className}`}>
      {(title || eyebrow || action) && (
        <div className="card-header">
          <div>
            {eyebrow && <div className="eyebrow">{eyebrow}</div>}
            {title && <div className="card-title">{title}</div>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow red">{eyebrow}</div>
        <div className="page-title">{title}</div>
        <div className="page-description">{description}</div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <ClipboardList size={26} />
      <div className="empty-title">Data not available yet</div>
      <div className="empty-copy">This section will populate after the next data refresh.</div>
    </div>
  );
}

function VideoFooter({ items }: { items: string[] }) {
  return (
    <footer className="video-footer">
      <div className="video-label"><CircleDot size={14} /> Check video for:</div>
      {items.map((item) => <span key={item}>{item}</span>)}
    </footer>
  );
}

function TrendIcon({ value }: { value: "up" | "down" | "flat" }) {
  if (value === "up") return <ArrowUp className="trend-up" size={13} />;
  if (value === "down") return <ArrowDown className="trend-down" size={13} />;
  return <ArrowRight className="trend-flat" size={13} />;
}

function PlayerPill({ player }: { player: SummaryData["forwardLines"][number][number] }) {
  return (
    <div className="lineup-player">
      <span className="position">{player.position}</span>
      <span className="player-name">{player.name}</span>
      <span className="toi">
        {player.toi.value}
        <TrendIcon value={player.trend.value} />
      </span>
      <span className="player-meta"><StatMeta stat={player.toi} /></span>
      <span className="player-meta trend-meta"><StatMeta stat={player.trend} /></span>
    </div>
  );
}

function CoachSummary({ data }: { data: PrescoutData["coach"]["summary"] }) {
  if (!data) return <EmptyState />;
  const quickStats = [
    { label: "Record", stat: data.record },
    { label: "Last 10", stat: data.lastTen },
    { label: "Rest", stat: data.restDays, suffix: " day" },
    { label: "Back-to-back", stat: data.backToBack, boolean: true },
  ];
  return (
    <div className="summary-screen">
      <div className="quick-strip">
        {quickStats.map((item) => (
          <div className="quick-stat" key={item.label}>
            <span className="quick-label">{item.label}</span>
            <StatValue
              stat={item.stat}
              className="quick-value"
              format={(value) => item.boolean ? (value ? "Yes" : "No") : `${String(value)}${item.suffix ?? ""}`}
            />
          </div>
        ))}
        <div className="quick-stat special">
          <span className="quick-label">Power play</span>
          <div className="rank-row"><StatValue stat={data.powerPlay} className="quick-value" /><span>{data.powerPlayRank.value}</span></div>
          <StatMeta stat={data.powerPlayRank} />
        </div>
        <div className="quick-stat special">
          <span className="quick-label">Penalty kill</span>
          <div className="rank-row"><StatValue stat={data.penaltyKill} className="quick-value" /><span>{data.penaltyKillRank.value}</span></div>
          <StatMeta stat={data.penaltyKillRank} />
        </div>
      </div>

      <div className="summary-main">
        <Card title="Keys to the game" eyebrow="Two-minute brief" className="keys-card">
          <div className="keys-grid">
            {data.keys.map((key, index) => (
              <div className="key-item" key={key.title}>
                <span className="key-index">{String(index + 1).padStart(2, "0")}</span>
                <div className="key-copy">
                  <div className="key-title">{key.title}</div>
                  <div className="key-insight">{key.insight}</div>
                </div>
                <StatValue stat={key.stat} className="key-stat" />
              </div>
            ))}
          </div>
        </Card>

        <div className="summary-right">
          <Card title="Likely starter" eyebrow="In net">
            <div className="goalie-row">
              <div className="goalie-mark"><Goal size={23} /></div>
              <div>
                <div className="goalie-name">{data.goalie.name}</div>
                <StatValue stat={data.goalie.startConfidence} className="starter-status" />
              </div>
            </div>
            <div className="goalie-stats">
              <div><span>Season SV%</span><StatValue stat={data.goalie.savePct} /></div>
              <div><span>Last 10 SV%</span><StatValue stat={data.goalie.lastTenSavePct} /></div>
            </div>
          </Card>
          <Card title="Projected lineup" eyebrow="Latest combinations" className="lineup-card">
            <div className="lineup-columns">
              <div>
                <div className="subheading">Forwards</div>
                {data.forwardLines.map((line, index) => (
                  <div className="line-row" key={`F${index}`}>
                    <span className="line-number">F{index + 1}</span>
                    {line.map((player) => <PlayerPill key={player.name} player={player} />)}
                  </div>
                ))}
              </div>
              <div>
                <div className="subheading">Defense</div>
                {data.defensePairs.map((pair, index) => (
                  <div className="line-row defense" key={`D${index}`}>
                    <span className="line-number">D{index + 1}</span>
                    {pair.map((player) => <PlayerPill key={player.name} player={player} />)}
                  </div>
                ))}
                <div className="trend-legend">
                  <span><ArrowUp size={12} /> TOI up</span>
                  <span><ArrowRight size={12} /> Flat</span>
                  <span><ArrowDown size={12} /> Down</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
      <VideoFooter items={data.videoChecks} />
    </div>
  );
}

function SpecialTeamsPage({ data }: { data: PrescoutData["coach"]["specialTeams"] }) {
  if (!data) return <EmptyState />;
  return (
    <>
      <PageHeader eyebrow="Coach report" title="Special Teams" description="Personnel, shot creation and penalty tendencies." />
      <div className="dashboard-grid two-one">
        <div className="stack">
          {data.powerPlayUnits.map((unit) => (
            <Card title={unit.name} eyebrow="Projected personnel" key={unit.name}>
              <div className="unit-row">
                {unit.players.map((player, index) => (
                  <div className="unit-player" key={player}><span>{index + 1}</span>{player}</div>
                ))}
              </div>
            </Card>
          ))}
          <Card title="Penalty profile" eyebrow="Taken vs drawn">
            <div className="data-table">
              <div className="table-row table-head"><span>Player</span><span>Taken</span><span>Drawn</span><span>Most likely</span></div>
              {data.penalties.map((row) => (
                <div className="table-row" key={row.player}>
                  <strong>{row.player}</strong>
                  <StatValue stat={row.taken} />
                  <StatValue stat={row.drawn} />
                  <StatValue stat={row.period} />
                </div>
              ))}
            </div>
          </Card>
        </div>
        <div className="stack">
          <Card title="Power-play shot map" eyebrow="Dot size = danger">
            <HalfRink points={data.shotMap} className="rink-chart" />
          </Card>
          <Card title="PK zone time" eyebrow="Average per opposition entry">
            <div className="comparison-stat">
              <div><span>Ottawa</span><StatValue stat={data.zoneTime} className="hero-stat" /></div>
              <div><span>League</span><StatValue stat={data.leagueZoneTime} className="hero-stat muted" /></div>
            </div>
          </Card>
        </div>
      </div>
      <VideoFooter items={data.videoChecks} />
    </>
  );
}

function FaceoffsPage({ data }: { data: PrescoutData["coach"]["faceoffs"] }) {
  if (!data) return <EmptyState />;
  return (
    <>
      <PageHeader eyebrow="Coach report" title="Faceoffs" description="Zone, strength and head-to-head matchup tendencies." />
      <div className="dashboard-grid">
        <Card title="Ottawa centers" eyebrow="Win percentage by situation" className="span-2">
          <div className="data-table centers">
            <div className="table-row table-head"><span>Center</span><span>Overall</span><span>OZ</span><span>NZ</span><span>DZ</span><span>5v5</span><span>PP</span><span>PK</span></div>
            {data.centers.map((center) => (
              <div className="table-row" key={center.name}>
                <strong>{center.name}</strong>
                {[center.overall, center.offensiveZone, center.neutralZone, center.defensiveZone, center.evenStrength, center.powerPlay, center.penaltyKill].map((stat, index) => <StatValue stat={stat} key={index} />)}
              </div>
            ))}
          </div>
        </Card>
        <Card title="OZ win → shot attempt" eyebrow="Within 10 seconds">
          <StatValue stat={data.postWinShotAttempts} className="standalone-stat" />
          <div className="callout-copy">Ottawa creates immediate offense on nearly one in three offensive-zone wins.</div>
        </Card>
        <Card title="Matchup matrix" eyebrow="Ottawa win percentage" className="span-3">
          <div className="matrix">
            <div className="matrix-row matrix-head"><span>Ottawa \\ Detroit</span>{data.detroitCenters.map((name) => <span key={name}>{name}</span>)}</div>
            {data.matchupMatrix.map((row) => (
              <div className="matrix-row" key={row.opponent}>
                <strong>{row.opponent}</strong>
                {row.values.map((stat, index) => <StatValue stat={stat} key={index} />)}
              </div>
            ))}
          </div>
        </Card>
      </div>
      <VideoFooter items={data.videoChecks} />
    </>
  );
}

function GoaliePage({ data }: { data: PrescoutData["coach"]["goalie"] }) {
  if (!data) return <EmptyState />;
  return (
    <>
      <PageHeader eyebrow="Coach report" title={data.name} description="Save profile, recent form and shot-type performance." />
      <div className="dashboard-grid goalie-grid">
        <Card title="Save percentage by zone" eyebrow="Season" className="net-card">
          <NetFront zones={data.zones.map((zone) => ({ label: zone.label, x: zone.x, y: zone.y, value: zone.stat.value }))} className="net-chart" />
          <div className="zone-meta">{data.zones.map((zone) => <div key={zone.label}><span>{zone.label}</span><StatMeta stat={zone.stat} /></div>)}</div>
        </Card>
        <Card title="Last 10 starts" eyebrow="Game-by-game save percentage" className="span-2">
          <div className="line-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.lastTen}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--line)" />
                <XAxis dataKey="label" tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis domain={["dataMin - 0.01", "dataMax + 0.01"]} tick={{ fill: "var(--muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "var(--panel-strong)", border: "1px solid var(--line)", borderRadius: "8px" }} />
                <Line type="monotone" dataKey="value" stroke="var(--red)" strokeWidth={3} dot={{ fill: "var(--red)", strokeWidth: 0, r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="Save percentage by shot type" eyebrow="Shot classification" className="span-3">
          <div className="shot-type-grid">
            {data.shotTypes.map((item) => <div key={item.type}><span>{item.type}</span><StatValue stat={item.stat} /></div>)}
          </div>
        </Card>
      </div>
      <VideoFooter items={data.videoChecks} />
    </>
  );
}

function GameStatePage({ data }: { data: PrescoutData["coach"]["gameState"] }) {
  if (!data) return <EmptyState />;
  const shotChart = data.shotRates.map((item) => ({ state: item.state, for: item.for.value, against: item.against.value }));
  const goalChart = data.goalsByPeriod.map((item) => ({ period: item.period, for: item.for.value, against: item.against.value }));
  return (
    <>
      <PageHeader eyebrow="Coach report" title="Game State" description="How Ottawa's behavior changes with the score and clock." />
      <div className="dashboard-grid">
        <Card title="Shot rates by score state" eyebrow="Attempts per 60" className="span-2">
          <div className="bar-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={shotChart}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--line)" />
                <XAxis dataKey="state" tick={{ fill: "var(--muted)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "var(--muted)" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "var(--panel-strong)", border: "1px solid var(--line)", borderRadius: "8px" }} />
                <Bar dataKey="for" fill="var(--red)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="against" fill="var(--slate)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-meta">{data.shotRates.map((row) => <span key={row.state}>{row.state}: <StatMeta stat={row.for} /> <StatMeta stat={row.against} /></span>)}</div>
        </Card>
        <Card title="Empty-net pull" eyebrow="Median trigger">
          <StatValue stat={data.emptyNetPull} className="standalone-stat compact" />
          <div className="benchmark"><span>League benchmark</span><StatValue stat={data.leagueEmptyNetPull} /></div>
        </Card>
        <Card title="Goals by period" eyebrow="For vs against" className="span-3">
          <div className="goals-layout">
            <div className="bar-chart short">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={goalChart} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--line)" />
                  <XAxis type="number" tick={{ fill: "var(--muted)" }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="period" tick={{ fill: "var(--muted)" }} axisLine={false} tickLine={false} />
                  <Bar dataKey="for" fill="var(--red)" radius={[0, 4, 4, 0]} />
                  <Bar dataKey="against" fill="var(--slate)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="period-meta">{data.goalsByPeriod.map((row) => <div key={row.period}><strong>{row.period}</strong><StatValue stat={row.for} /><StatValue stat={row.against} /></div>)}</div>
          </div>
        </Card>
      </div>
      <VideoFooter items={data.videoChecks} />
    </>
  );
}

function PlayerTargetsPage({ data }: { data: PrescoutData["coach"]["playerTargets"] }) {
  if (!data) return <EmptyState />;
  return (
    <>
      <PageHeader eyebrow="Coach report" title="Player Targets" description="Clear, actionable matchups for the room." />
      <div className="target-columns">
        <Card title="Pressure these players" eyebrow="Turnover-prone defensemen">
          <div className="target-list">
            {data.pressure.map((player, index) => (
              <div className="target-row" key={player.name}>
                <div className="target-number">{index + 1}</div>
                <div className="target-copy"><div><strong>{player.name}</strong><span>{player.position}</span></div><p>{player.forecheckNote}</p></div>
                <div className="target-stat"><span>Giveaways</span><StatValue stat={player.giveaways} /></div>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Watch these players" eyebrow="Speed and shooting threats">
          <div className="target-list">
            {data.watch.map((player, index) => (
              <div className="target-row" key={player.name}>
                <div className="target-number danger">{index + 1}</div>
                <div className="target-copy"><div><strong>{player.name}</strong><span>{player.position}</span></div><p>{player.threatNote}</p></div>
                <div className="dual-target-stat"><div><span>Top speed</span><StatValue stat={player.topSpeed} /></div><div><span>Shot speed</span><StatValue stat={player.shotSpeed} /></div></div>
              </div>
            ))}
          </div>
        </Card>
      </div>
      <VideoFooter items={data.videoChecks} />
    </>
  );
}

function GmSummaryPage({ data }: { data: PrescoutData["gm"] }) {
  const summary = data.summary;
  if (!summary && !data.rosterChanges && !data.standings && !data.headToHead) return <EmptyState />;
  return (
    <>
      <PageHeader eyebrow="Front office report" title="GM Summary" description="Sustainability, roster context and the playoff picture." />
      <div className="gm-layout">
        <Card title="Is this team for real?" eyebrow="Performance vs expected" className="span-2">
          {summary ? (
            <div className="sustainability">
              <div className="sustain-pair"><span>Shooting</span><StatValue stat={summary.sustainability.shootingPct} className="hero-stat" /><div>Expected <StatValue stat={summary.sustainability.expectedShootingPct} /></div></div>
              <div className="sustain-pair"><span>Save percentage</span><StatValue stat={summary.sustainability.savePct} className="hero-stat" /><div>Expected <StatValue stat={summary.sustainability.expectedSavePct} /></div></div>
              <div className="sustain-pair"><span>PDO</span><StatValue stat={summary.sustainability.pdo} className="hero-stat" /><div>Expected <StatValue stat={summary.sustainability.expectedPdo} /></div></div>
              <div className="regression-box"><TrendingUp size={20} /><div><span>Regression outlook</span><StatValue stat={summary.sustainability.regressionFlag} /></div></div>
            </div>
          ) : <EmptyState />}
        </Card>
        <Card title="Standings impact" eyebrow="Today">
          {data.standings ? (
            <><div className="standings-numbers"><div><span>Points pace</span><StatValue stat={data.standings.pointsPace} className="standalone-stat compact" /></div><div><span>Playoff line</span><StatValue stat={data.standings.playoffGap} className="standalone-stat compact" /></div></div><div className="meaning"><strong>For Ottawa</strong><p>{data.standings.opponentMeaning}</p><strong>For Detroit</strong><p>{data.standings.detroitMeaning}</p></div></>
          ) : <EmptyState />}
        </Card>
        <Card title="Last five games: roster movement" eyebrow="Availability signals" className="span-2">
          {data.rosterChanges ? (
            <div className="timeline">{data.rosterChanges.changes.map((change) => <div className="timeline-row" key={`${change.date}-${change.player}`}><span className="timeline-date">{change.date}</span><span className="timeline-dot" /><div><strong>{change.player}</strong><span>{change.change}</span><p>{change.detail}</p></div><StatValue stat={change.status} /></div>)}</div>
          ) : <EmptyState />}
        </Card>
        <Card title="Head-to-head" eyebrow="Recent meetings">
          {data.headToHead ? (
            <div className="meetings">{data.headToHead.meetings.map((meeting) => <div className="meeting" key={`${meeting.season}-${meeting.date}`}><div><span>{meeting.season} · {meeting.date}</span><strong>{meeting.result}</strong></div><div><span>Shots</span><StatValue stat={meeting.shots} /></div><div><span>xG</span><StatValue stat={meeting.expectedGoals} /></div><div><span>Special teams</span><StatValue stat={meeting.specialTeams} /></div></div>)}</div>
          ) : <EmptyState />}
        </Card>
      </div>
      {summary && <VideoFooter items={summary.videoChecks} />}
    </>
  );
}

function PlayerEvaluationPage({ players }: { players: PrescoutData["gm"]["players"] }) {
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState<"name" | "position" | "age">("name");
  const [selectedId, setSelectedId] = useState<string | null>(players?.[0]?.id ?? null);
  const [watchList, setWatchList] = useState<string[]>([]);
  const filtered = useMemo(() => {
    if (!players) return [];
    return players
      .filter((player) => player.name.toLowerCase().includes(query.toLowerCase()) || player.position.toLowerCase().includes(query.toLowerCase()))
      .sort((a, b) => sortKey === "age" ? a.age.value - b.age.value : a[sortKey].localeCompare(b[sortKey]));
  }, [players, query, sortKey]);
  const selected = players?.find((player) => player.id === selectedId) ?? filtered[0];

  if (!players) return <EmptyState />;
  return (
    <>
      <PageHeader eyebrow="Front office report" title="Player Evaluation" description="Opponent personnel profiles and live scouting notes." />
      <div className="player-eval">
        <Card className="player-list-card">
          <div className="search-box"><Search size={16} /><TextInput value={query} onChange={setQuery} placeholder="Search players" />{query && <Button ariaLabel="Clear search" onClick={() => setQuery("")}><X size={15} /></Button>}</div>
          <div className="sort-row"><span>Sort by</span>{(["name", "position", "age"] as const).map((key) => <Button key={key} onClick={() => setSortKey(key)} className={sortKey === key ? "active" : ""}>{key}</Button>)}</div>
          <div className="player-list">
            {filtered.map((player) => (
              <Button key={player.id} onClick={() => setSelectedId(player.id)} className={`player-list-item ${selected?.id === player.id ? "selected" : ""}`}>
                <div className="avatar">{player.name.split(" ").map((part) => part[0]).join("")}</div>
                <div><strong>{player.name}</strong><span>{player.position}</span></div>
                <ChevronRight size={16} />
              </Button>
            ))}
          </div>
        </Card>
        {selected && <PlayerProfile player={selected} saved={watchList.includes(selected.id)} onSave={() => setWatchList((current) => current.includes(selected.id) ? current.filter((id) => id !== selected.id) : [...current, selected.id])} />}
      </div>
    </>
  );
}

function PlayerProfile({ player, saved, onSave }: { player: GmPlayer; saved: boolean; onSave: () => void }) {
  return (
    <div className="profile-stack">
      <Card className="profile-hero">
        <div className="profile-title">
          <div className="avatar large">{player.name.split(" ").map((part) => part[0]).join("")}</div>
          <div><div className="eyebrow">Opponent profile</div><div className="profile-name">{player.name}</div><div className="profile-sub">{player.position} · Age <StatValue stat={player.age} /></div></div>
        </div>
        <Button className={`watch-button ${saved ? "saved" : ""}`} onClick={onSave}><Star size={16} fill={saved ? "currentColor" : "none"} />{saved ? "Saved to watch list" : "Save to watch list"}</Button>
      </Card>
      <div className="profile-grid">
        <Card title="Usage" eyebrow="Time on ice by strength">
          <div className="usage-grid"><div><span>Even strength</span><StatValue stat={player.toi.evenStrength} /></div><div><span>Power play</span><StatValue stat={player.toi.powerPlay} /></div><div><span>Penalty kill</span><StatValue stat={player.toi.penaltyKill} /></div></div>
        </Card>
        <Card title="On-ice results" eyebrow="Season">
          <div className="results-grid"><div><span>Zone starts</span><StatValue stat={player.zoneStarts} /></div><div><span>Goals share</span><StatValue stat={player.onIceGoalsPct} /></div><div><span>Expected goals</span><StatValue stat={player.onIceExpectedGoalsPct} /></div></div>
        </Card>
        <Card title="Tracking" eyebrow="Peak readings">
          <div className="tracking-grid"><div><Gauge size={18} /><span>Top speed</span><StatValue stat={player.topSpeed} /></div><div><Target size={18} /><span>Shot speed</span><StatValue stat={player.shotSpeed} /></div></div>
        </Card>
        <Card title="Shot locations" eyebrow="Season" className="shot-map-card">
          <HalfRink points={player.shotMap} className="rink-chart profile-rink" />
        </Card>
        <Card title="Scouting notes" eyebrow="Internal" className="notes-card"><p>{player.notes}</p></Card>
      </div>
    </div>
  );
}

function AppShell({ data }: { data: PrescoutData }) {
  const [mode, setMode] = useState<Mode>("coach");
  const [page, setPage] = useState<Page>("summary");
  const nav = mode === "coach" ? coachNav : gmNav;
  const gameDate = new Intl.DateTimeFormat("en-US", { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(data.meta.gameDate));

  const switchMode = (next: Mode) => {
    setMode(next);
    setPage(next === "coach" ? "summary" : "gmSummary");
  };

  const content = () => {
    switch (page) {
      case "summary": return <CoachSummary data={data.coach.summary} />;
      case "specialTeams": return <SpecialTeamsPage data={data.coach.specialTeams} />;
      case "faceoffs": return <FaceoffsPage data={data.coach.faceoffs} />;
      case "goalie": return <GoaliePage data={data.coach.goalie} />;
      case "gameState": return <GameStatePage data={data.coach.gameState} />;
      case "playerTargets": return <PlayerTargetsPage data={data.coach.playerTargets} />;
      case "gmSummary": return <GmSummaryPage data={data.gm} />;
      case "players": return <PlayerEvaluationPage players={data.gm.players} />;
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">PS</div><div><strong>Pre-Scout</strong><span>Hockey intelligence</span></div></div>
        <div className="mode-label">{mode === "coach" ? "Coaching staff" : "Front office"}</div>
        <nav className="nav-list">
          {nav.map((item) => {
            const Icon = item.icon;
            return <Button key={item.id} onClick={() => setPage(item.id)} className={`nav-item ${page === item.id ? "active" : ""}`}><Icon size={17} /><span>{item.label}</span>{page === item.id && <span className="nav-active-mark" />}</Button>;
          })}
        </nav>
        <div className="sidebar-bottom">
          <div className="data-status"><span className="status-dot" /><div><strong>Report current</strong><span>Through {data.meta.dataThroughDate}</span></div></div>
          <div className="version">Schema v{data.meta.schemaVersion}</div>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div className="opponent-block">
            <span>Next opponent</span>
            <div><strong>{data.meta.opponent}</strong><span className="game-chip">{data.meta.homeAway === "home" ? "Home" : "Away"}</span></div>
          </div>
          <div className="topbar-right">
            <div className="game-time"><span>{gameDate}</span><small>Report generated {new Date(data.meta.generatedAt).toLocaleDateString()}</small></div>
            <div className="mode-toggle">
              <Button className={mode === "coach" ? "active" : ""} onClick={() => switchMode("coach")}>Coach</Button>
              <Button className={mode === "gm" ? "active" : ""} onClick={() => switchMode("gm")}>GM</Button>
            </div>
            <Button className="export-button" onClick={() => window.print()}><Download size={15} />Export PDF</Button>
          </div>
        </header>
        <main className={`main-content ${page === "summary" ? "summary-content" : ""}`}>{content()}</main>
      </div>
    </div>
  );
}

export default function App() {
  const [data, setData] = useState<PrescoutData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch("/data/latest.json")
      .then((response) => {
        if (!response.ok) throw new Error("Report request failed");
        return response.json() as Promise<PrescoutData>;
      })
      .then(setData)
      .catch(() => setError(true));
  }, []);

  if (error) return <div className="load-state"><X size={28} /><strong>Unable to load report</strong><span>Check the data file and refresh.</span></div>;
  if (!data) return <div className="load-state"><div className="loader" /><strong>Loading pre-scout</strong><span>Building the latest opponent report.</span></div>;
  return <AppShell data={data} />;
}
