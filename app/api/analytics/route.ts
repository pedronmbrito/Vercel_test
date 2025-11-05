import { NextResponse } from 'next/server'
import { getAllUrls } from '@/lib/db'

export async function GET() {
  try {
    const urls = getAllUrls()

    // Sort by creation date (newest first)
    const sortedUrls = urls.sort((a, b) =>
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )

    return NextResponse.json({
      urls: sortedUrls,
      totalUrls: urls.length,
      totalClicks: urls.reduce((sum, url) => sum + url.clicks, 0),
    })
  } catch (error) {
    console.error('Error fetching analytics:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
