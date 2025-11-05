import { NextRequest, NextResponse } from 'next/server'
import { nanoid } from 'nanoid'
import { createShortUrl, shortIdExists } from '@/lib/db'

export async function POST(request: NextRequest) {
  try {
    const { url } = await request.json()

    if (!url) {
      return NextResponse.json(
        { error: 'URL is required' },
        { status: 400 }
      )
    }

    // Validate URL
    try {
      new URL(url)
    } catch {
      return NextResponse.json(
        { error: 'Invalid URL format' },
        { status: 400 }
      )
    }

    // Generate unique short ID
    let shortId = nanoid(6)
    while (shortIdExists(shortId)) {
      shortId = nanoid(6)
    }

    // Save to database
    createShortUrl(url, shortId)

    // Get the base URL
    const baseUrl = request.nextUrl.origin

    return NextResponse.json({
      shortUrl: `${baseUrl}/${shortId}`,
      shortId,
      originalUrl: url,
    })
  } catch (error) {
    console.error('Error shortening URL:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
