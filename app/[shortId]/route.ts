import { NextRequest, NextResponse } from 'next/server'
import { getUrlByShortId, incrementClicks } from '@/lib/db'

export async function GET(
  request: NextRequest,
  { params }: { params: { shortId: string } }
) {
  const { shortId } = params

  const urlEntry = getUrlByShortId(shortId)

  if (!urlEntry) {
    return new NextResponse('Short URL not found', { status: 404 })
  }

  // Increment click count
  incrementClicks(shortId)

  // Redirect to original URL
  return NextResponse.redirect(urlEntry.originalUrl, { status: 307 })
}
