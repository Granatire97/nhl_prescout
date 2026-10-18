export type Confidence = "high" | "medium" | "low";

export interface Stat<T> {
  value: T;
  sampleSize: number;
  confidence: Confidence;
  isEstimate?: boolean;
}

export interface RinkPoint {
  x: number;
  y: number;
  danger: number;
}

export interface TrendPoint {
  label: string;
  value: number;
}

export interface PlayerLineupEntry {
  name: string;
  position: string;
  toi: Stat<string>;
  trend: Stat<"up" | "down" | "flat">;
}

export interface SummaryData {
  record: Stat<string>;
  lastTen: Stat<string>;
  restDays: Stat<number>;
  backToBack: Stat<boolean>;
  keys: Array<{ title: string; insight: string; stat: Stat<string> }>;
  forwardLines: PlayerLineupEntry[][];
  defensePairs: PlayerLineupEntry[][];
  goalie: {
    name: string;
    savePct: Stat<string>;
    lastTenSavePct: Stat<string>;
    startConfidence: Stat<string>;
  };
  powerPlay: Stat<string>;
  powerPlayRank: Stat<string>;
  penaltyKill: Stat<string>;
  penaltyKillRank: Stat<string>;
  videoChecks: string[];
}

export interface SpecialTeamsData {
  powerPlayUnits: Array<{ name: string; players: string[] }>;
  shotMap: RinkPoint[];
  zoneTime: Stat<string>;
  leagueZoneTime: Stat<string>;
  penalties: Array<{
    player: string;
    taken: Stat<number>;
    drawn: Stat<number>;
    period: Stat<string>;
  }>;
  videoChecks: string[];
}

export interface FaceoffsData {
  centers: Array<{
    name: string;
    overall: Stat<string>;
    offensiveZone: Stat<string>;
    neutralZone: Stat<string>;
    defensiveZone: Stat<string>;
    evenStrength: Stat<string>;
    powerPlay: Stat<string>;
    penaltyKill: Stat<string>;
  }>;
  detroitCenters: string[];
  matchupMatrix: Array<{
    opponent: string;
    values: Stat<string>[];
  }>;
  postWinShotAttempts: Stat<string>;
  videoChecks: string[];
}

export interface GoalieData {
  name: string;
  zones: Array<{ label: string; x: number; y: number; stat: Stat<string> }>;
  lastTen: TrendPoint[];
  shotTypes: Array<{ type: string; stat: Stat<string> }>;
  videoChecks: string[];
}

export interface GameStateData {
  shotRates: Array<{
    state: string;
    for: Stat<number>;
    against: Stat<number>;
  }>;
  goalsByPeriod: Array<{
    period: string;
    for: Stat<number>;
    against: Stat<number>;
  }>;
  emptyNetPull: Stat<string>;
  leagueEmptyNetPull: Stat<string>;
  videoChecks: string[];
}

export interface PlayerTargetsData {
  pressure: Array<{
    name: string;
    position: string;
    giveaways: Stat<number>;
    forecheckNote: string;
  }>;
  watch: Array<{
    name: string;
    position: string;
    topSpeed: Stat<string>;
    shotSpeed: Stat<string>;
    threatNote: string;
  }>;
  videoChecks: string[];
}

export interface GmSummaryData {
  sustainability: {
    shootingPct: Stat<string>;
    expectedShootingPct: Stat<string>;
    savePct: Stat<string>;
    expectedSavePct: Stat<string>;
    pdo: Stat<number>;
    expectedPdo: Stat<number>;
    regressionFlag: Stat<string>;
  };
  videoChecks: string[];
}

export interface RosterChangesData {
  changes: Array<{
    date: string;
    player: string;
    change: string;
    detail: string;
    status: Stat<string>;
  }>;
}

export interface StandingsData {
  pointsPace: Stat<number>;
  playoffGap: Stat<string>;
  opponentMeaning: string;
  detroitMeaning: string;
}

export interface HeadToHeadData {
  meetings: Array<{
    season: string;
    date: string;
    result: string;
    shots: Stat<string>;
    expectedGoals: Stat<string>;
    specialTeams: Stat<string>;
  }>;
}

export interface GmPlayer {
  id: string;
  name: string;
  position: string;
  age: Stat<number>;
  toi: {
    evenStrength: Stat<string>;
    powerPlay: Stat<string>;
    penaltyKill: Stat<string>;
  };
  zoneStarts: Stat<string>;
  onIceGoalsPct: Stat<string>;
  onIceExpectedGoalsPct: Stat<string>;
  topSpeed: Stat<string>;
  shotSpeed: Stat<string>;
  shotMap: RinkPoint[];
  notes: string;
}

export interface PrescoutData {
  meta: {
    schemaVersion: string;
    generatedAt: string;
    team: string;
    opponent: string;
    gameDate: string;
    homeAway: "home" | "away";
    dataThroughDate: string;
  };
  coach: {
    summary: SummaryData | null;
    specialTeams: SpecialTeamsData | null;
    faceoffs: FaceoffsData | null;
    goalie: GoalieData | null;
    gameState: GameStateData | null;
    playerTargets: PlayerTargetsData | null;
  };
  gm: {
    summary: GmSummaryData | null;
    rosterChanges: RosterChangesData | null;
    standings: StandingsData | null;
    headToHead: HeadToHeadData | null;
    players: GmPlayer[] | null;
  };
}
