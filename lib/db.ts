import { readFileSync, writeFileSync, existsSync } from 'fs'
import { join } from 'path'

export interface UrlEntry {
  id: string
  originalUrl: string
  shortId: string
  clicks: number
  createdAt: string
  lastClickedAt?: string
}

const DB_FILE = join(process.cwd(), 'data', 'urls.json')

function ensureDataDir() {
  const dataDir = join(process.cwd(), 'data')
  if (!existsSync(dataDir)) {
    const { mkdirSync } = require('fs')
    mkdirSync(dataDir, { recursive: true })
  }
}

function readDB(): UrlEntry[] {
  ensureDataDir()

  if (!existsSync(DB_FILE)) {
    writeFileSync(DB_FILE, JSON.stringify([]))
    return []
  }

  try {
    const data = readFileSync(DB_FILE, 'utf-8')
    return JSON.parse(data)
  } catch (error) {
    return []
  }
}

function writeDB(data: UrlEntry[]) {
  ensureDataDir()
  writeFileSync(DB_FILE, JSON.stringify(data, null, 2))
}

export function createShortUrl(originalUrl: string, shortId: string): UrlEntry {
  const urls = readDB()

  const entry: UrlEntry = {
    id: Date.now().toString(),
    originalUrl,
    shortId,
    clicks: 0,
    createdAt: new Date().toISOString(),
  }

  urls.push(entry)
  writeDB(urls)

  return entry
}

export function getUrlByShortId(shortId: string): UrlEntry | null {
  const urls = readDB()
  return urls.find(url => url.shortId === shortId) || null
}

export function incrementClicks(shortId: string): void {
  const urls = readDB()
  const urlIndex = urls.findIndex(url => url.shortId === shortId)

  if (urlIndex !== -1) {
    urls[urlIndex].clicks++
    urls[urlIndex].lastClickedAt = new Date().toISOString()
    writeDB(urls)
  }
}

export function getAllUrls(): UrlEntry[] {
  return readDB()
}

export function shortIdExists(shortId: string): boolean {
  const urls = readDB()
  return urls.some(url => url.shortId === shortId)
}
