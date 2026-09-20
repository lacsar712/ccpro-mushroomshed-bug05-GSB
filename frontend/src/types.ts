export type RoomStatus = 'fruiting' | 'idle' | 'sanitize'
export type HarvestGrade = 'A' | 'B' | 'C'

export interface Shed {
  id: number
  name: string
  location: string
  notes?: string | null
}

export interface Room {
  id: number
  shedId: number
  roomCode: string
  species: string
  capacityBags: number
  status: RoomStatus
}

export interface ClimateLog {
  id: number
  roomId: number
  recordedAt: string
  tempC: number
  humidityPct: number
  co2Ppm?: number | null
  notes?: string | null
}

export interface FlushHarvest {
  id: number
  roomId: number
  harvestedAt: string
  flushNo: number
  weightKg: number
  grade: HarvestGrade
  operatorName: string
}

export interface DashboardStats {
  shedTotal: number
  fruitingRoomCount: number
  climateLast24h: number
  harvestKgLast7d: number
}
