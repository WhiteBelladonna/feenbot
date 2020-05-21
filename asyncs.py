#asyncio_echo_server_protocol.py
class EchoServer(asyncio.Protocol):

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(name)s: %(message)s',
            stream=sys.stderr,
        )
        log = logging.getLogger('main')

    async def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.log = logging.getLogger(
            'EchoServer_{}_{}'.format(*self.address)
        )
        self.log.debug('connection accepted')

    async def data_received(self, data):
        self.log.debug('received {!r}'.format(data))
        self.transport.write(data)
        self.log.debug('sent {!r}'.format(data))
        await newTable(data)

    async def eof_received(self):
        self.log.debug('received EOF')
        if self.transport.can_write_eof():
            self.transport.write_eof()

    async def connection_lost(self, error):
        if error:
            self.log.error('ERROR: {}'.format(error))
        else:
            self.log.debug('closing')
        super().connection_lost(error)