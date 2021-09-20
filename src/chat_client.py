import asyncio
import logging
import socket
import websockets
import websockets.client
import argparse
import sys


def _get_arg_parser():
    parser = argparse.ArgumentParser(description='Start simple chat client')
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


async def run_async(host, port):
    async with websockets.client.connect(f'ws://{host}:{port}') as conn:
        async for msg_in in conn:
            logging.info(f'Received msg ({type(msg_in)}): {msg_in}')
    logging.info('DONE')


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
    logger.debug(f'connecting to {host}:{port}')
    conn.connect((host, port))
    logger.debug(f'connecting to {host}:{port} DONE')

    def prompt_input():
        return input('Send msg : ')

    msg_out = prompt_input()
    while msg_out.lower() != 'exit' and msg_out.lower() != 'quit':
        conn.sendall(bytes(msg_out, 'utf-8'))
        msg_in = conn.recv(buffer_size)
        logger.info(
            f'''Received msg: {msg_in.decode('utf-8')}\
        \n\tlocal_addr   : {conn.getsockname()}\
        \n\tforeign_addr : {conn.getpeername()}''')
        msg_out = prompt_input()
    # Tell the server that we are disconnecting (so it doesn't think the connection dropped due to an error)
    conn.close()


if __name__ == '__main__':
    main()
