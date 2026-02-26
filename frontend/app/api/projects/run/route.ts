import { NextRequest, NextResponse } from 'next/server'
import axios from 'axios'
import * as path from 'path'
import * as fs from 'fs'

const API_KEY = process.env.PARSEHUB_API_KEY || ''
const BASE_URL = process.env.PARSEHUB_BASE_URL || 'https://www.parsehub.com/api/v2'

function saveRunToken(token: string, runToken: string) {
  try {
    const filePath = path.join(process.cwd(), '..', 'active_runs.json')
    let data: any = {
      timestamp: new Date().toISOString(),
      runs: []
    }
    
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8')
      data = JSON.parse(content)
    }
    
    if (!Array.isArray(data.runs)) {
      data.runs = []
    }
    
    // Add or update the run token
    const existingIndex = data.runs.findIndex((r: any) => r.token === token)
    if (existingIndex >= 0) {
      data.runs[existingIndex].run_token = runToken
      data.runs[existingIndex].status = 'started'
    } else {
      data.runs.push({
        token,
        run_token: runToken,
        status: 'started',
        project: token,
      })
    }
    
    data.timestamp = new Date().toISOString()
    
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
    console.log(`Saved run token for project ${token}: ${runToken}`)
    return true
  } catch (error) {
    console.error('Error saving run token:', error)
    return false
  }
}

export async function POST(request: NextRequest) {
  try {
    const { token, project_token, pages } = await request.json()
    
    // Accept either 'token' or 'project_token' field name
    const projectToken = token || project_token

    if (!projectToken) {
      return NextResponse.json(
        { error: 'Project token is required' },
        { status: 400 }
      )
    }

    console.log(`[API] Running project: ${projectToken} with ${pages || 1} pages`)

    const response = await axios.post(
      `${BASE_URL}/projects/${projectToken}/run`,
      {},
      { params: { api_key: API_KEY, pages: pages || 1 } }
    )

    if (response.data && response.data.run_token) {
      saveRunToken(projectToken, response.data.run_token)
      
      // Save pages info to active_runs.json if pages specified
      if (pages && pages > 0) {
        try {
          const filePath = path.join(process.cwd(), '..', 'active_runs.json')
          let data: any = { timestamp: new Date().toISOString(), runs: [] }
          
          if (fs.existsSync(filePath)) {
            const content = fs.readFileSync(filePath, 'utf-8')
            data = JSON.parse(content)
          }
          
          if (!Array.isArray(data.runs)) {
            data.runs = []
          }
          
          const runIndex = data.runs.findIndex((r: any) => r.token === projectToken && r.run_token === response.data.run_token)
          if (runIndex >= 0) {
            data.runs[runIndex].target_pages = pages
          }
          
          data.timestamp = new Date().toISOString()
          fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
        } catch (err) {
          console.log('Warning: Could not save pages info:', err)
        }
      }
    }

    console.log(`[API] ✅ Project run started: ${projectToken}, run_token: ${response.data.run_token}`)

    return NextResponse.json({
      success: true,
      run_token: response.data.run_token,
      status: 'started',
      pages: pages || 1,
    })
  } catch (error) {
    console.error('[API] Error running project:', error)
    
    if (axios.isAxiosError(error)) {
      console.error('[API] Error response:', error.response?.data)
      return NextResponse.json(
        { error: error.response?.data?.error || error.message || 'Failed to run project' },
        { status: error.response?.status || 500 }
      )
    }

    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to run project' },
      { status: 500 }
    )
  }
}
