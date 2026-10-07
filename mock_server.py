import asyncio
from aiohttp import web

async def stream_handler(request):
    try:
        data = await request.json()
        prompt = data.get('messages', [{}])[0].get('content', '')
    except Exception:
        prompt = ''
        
    if 'fail' in prompt:
        return web.Response(status=500, text="Simulated Internal Server Error")

    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )
    await response.prepare(request)

    if 'empty' in prompt:
        # Returns [DONE] immediately with NO choices and NO usage
        await response.write(b'data: [DONE]\n\n')
        await response.write_eof()
        return response

    if 'single' in prompt:
        await asyncio.sleep(0.1)
        await response.write(b'data: {"id": "1", "choices": [{"delta": {"content": "One"}}]}\n\n')
        await response.write(b'data: {"id": "1", "usage": {"completion_tokens": 1}}\n\n')
        await response.write(b'data: [DONE]\n\n')
        await response.write_eof()
        return response

    # Default behaviour (or 'absent')
    await asyncio.sleep(0.2)
    await response.write(b'data: {"id": "1", "choices": [{"delta": {"content": "Hello"}}]}\n\n')

    for i in range(10):
        await asyncio.sleep(0.045)
        await response.write(b'data: {"id": "1", "choices": [{"delta": {"content": " world"}}]}\n\n')

    if 'absent' not in prompt:
        await response.write(b'data: {"id": "1", "usage": {"completion_tokens": 11}}\n\n')
    
    await response.write(b'data: [DONE]\n\n')
    await response.write_eof()
    return response

app = web.Application()
app.router.add_post('/v1/chat/completions', stream_handler)

if __name__ == '__main__':
    print("Starting Mock VLLM Streaming Server on port 8081...")
    web.run_app(app, port=8081)
