
"""
Abyss Diver Local Image Generation API

Coded by @SPOOKEXE
"""

from fastapi import FastAPI

from webapi import app

import asyncio
import uvicorn

async def uvicorn_run(app : FastAPI, host : str = "127.0.0.1", port : int = 8000) -> None:
	config = uvicorn.Config(app, host=host, port=port, access_log=False, server_header=False, date_header=False, proxy_headers=False)
	await uvicorn.Server(config).serve()

async def main(host : str = '127.0.0.1', port : int = 8000) -> None:
	await uvicorn_run(app, host=host, port=port)

if __name__ == '__main__':
	asyncio.run(main(host='127.0.0.1', port=8000))
