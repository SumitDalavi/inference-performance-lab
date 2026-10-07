import asyncio
from aiohttp import web

async def stream_handler(request):
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

    # Mock TTFT (Time To First Token) delay: 200ms
    await asyncio.sleep(0.2)
    await response.write(b'data: {"id": "1", "choices": [{"delta": {"content": "Hello"}}]}\n\n')

    # Mock ITL (Inter-Token Latency): 45ms per chunk
    for i in range(10):
        await asyncio.sleep(0.045)
        await response.write(b'data: {"id": "1", "choices": [{"delta": {"content": " world"}}]}\n\n')

    await response.write(b'data: [DONE]\n\n')
    await response.write_eof()
    return response

app = web.Application()
app.router.add_post('/v1/chat/completions', stream_handler)

if __name__ == '__main__':
    print("Starting Mock VLLM Streaming Server on port 8081...")
    web.run_app(app, port=8081)
