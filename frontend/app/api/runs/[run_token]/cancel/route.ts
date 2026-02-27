import { NextRequest } from 'next/server';
import { proxyToBackend } from '../../../_proxy';

export async function POST(
  request: NextRequest,
  { params }: { params: { run_token: string } }
) {
  return proxyToBackend(request, `/api/runs/${params.run_token}/cancel`);
}
