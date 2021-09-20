import asyncio
import logging
import socket
import argparse
import sys
import websockets
import websockets.server


def _get_arg_parser():
    parser = argparse.ArgumentParser(description='Start simple chat server')
    parser.add_argument(
        '--port',
        metavar='port',
        type=int,
        nargs='?',
        help='The port to which to connect',
        default=5678)

    parser.add_argument(
        '--host',
        metavar='host',
        type=str,
        nargs='?',
        help='The host to which to connect',
        default='localhost')

    parser.add_argument(
        '--verbosity',
        metavar='verbosity',
        type=int,
        nargs='?',
        choices=[logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR],
        help='The verbosity level',
        default=logging.INFO)

    parser.add_argument(
        '--async',
        action='store_true',
        help='Whether or not to run asynchronously')
    return parser


def _init_logger(verbosity):
    logger = logging.getLogger()
    logger.setLevel(verbosity)
    # print logs to console
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger


async def run_async(host, port, n_msgs=3, sleep_interval=3):
    async def ws_handler(
            protocol: websockets.server.WebSocketServerProtocol, path):
        for i in range(1, n_msgs + 1):
            logging.info(f'conn sending msg {i}...')
            await protocol.send(f'msg {i}')
            await asyncio.sleep(sleep_interval)

    async with websockets.server.serve(ws_handler, host, port) as conn:
        logging.info(
            'connection established.  Now waiting for connection to close...')
        await conn.wait_closed()
        logging.info('connection closed. DONE')


def main():
    parser = _get_arg_parser()
    args = parser.parse_args()
    host = args.host
    port = args.port
    buffer_size = 1024

    logger = _init_logger(args.verbosity)
    if vars(args)['async']:
        asyncio.run(run_async(host, port))
        return

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reserve port for this socket (once 'bind' is called, other sockets won't be allowed to use this port)
    conn.bind((host, port))
    # put socket in 'listen' mode
    conn.listen(1)
    # accept incoming connection (i.e., from the client).  This will block until the connection is made
    (conn_in, addr_in) = conn.accept()

    # receive msg from client.  This will block until a message is received
    msg_in = conn_in.recv(buffer_size)
    while msg_in:
        msg_in_str = msg_in.decode('utf-8')
        logger.info(
            f'''Received msg: {msg_in_str}\
        \n\tlocal_addr   : {conn_in.getsockname()}\
        \n\tforeign_addr : {addr_in}''')
        conn_in.sendall(f'{msg_in_str} - copy that'.encode('utf-8'))
        msg_in = conn_in.recv(buffer_size)


if __name__ == '__main__':
    main()
