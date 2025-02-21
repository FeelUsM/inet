import asyncio

async def handle_client(reader, writer):
    client_address = writer.get_extra_info('peername')
    print(f"{client_address[0]}:{client_address[1]} подключился")
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"{client_address[0]}:{client_address[1]} > {message}")
    except asyncio.CancelledError:
        pass
    finally:
        print(f"{client_address[0]}:{client_address[1]} отключился")
        writer.close()
        await writer.wait_closed()

async def start_server(host='0.0.0.0', port=80):
    server = await asyncio.start_server(handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f"Сервер слушает {addr[0]}:{addr[1]}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())
