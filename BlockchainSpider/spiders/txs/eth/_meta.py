import scrapy

from BlockchainSpider.utils.apikey import JsonAPIKeyBucket
from BlockchainSpider.utils.url import QueryURLBuilder


class TxsETHSpider(scrapy.Spider):
    # Target original url configure
    TXS_API_URL = 'https://api-cn.etherscan.com/api'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # input source nodes
        self.source = kwargs.get('source', None)
        self.filename = kwargs.get('file', None)
        assert self.source or self.filename, "`source` or `file` arguments are needed"

        # output dir
        self.out_dir = kwargs.get('out', './data')
        self.out_fields = kwargs.get('fields', 'hash,from,to,value,timeStamp,blockNumber').split(',')

        # apikey bucket
        self.apikey_bucket = JsonAPIKeyBucket('eth')

        # tx types
        self.txs_types = kwargs.get('types', 'external').split(',')
        self.txs_req_getter = {
            'external': self.get_external_txs_request,
            'internal': self.get_internal_txs_request,
            'erc20': self.get_erc20_txs_request,
            'erc721': self.get_erc721_txs_request,
        }
        for txs_type in self.txs_types:
            assert txs_type in set(self.txs_req_getter.keys())

        # tx block range
        self.start_blk = int(kwargs.get('start_blk', 0))
        self.end_blk = int(kwargs.get('end_blk', 99999999))

        # auto turn page, for the etherscan api offer 10k txs per request
        self.auto_page = kwargs.get('auto_page', True)
        self.auto_page = False if self.auto_page == 'False' else True

    def get_max_blk(self, txs: list):
        rlt = 0
        for tx in txs:
            blk_num = int(tx.get('blockNumber', 0))
            if blk_num > rlt:
                rlt = blk_num
        return rlt

    def get_external_txs_request(self, address: str, **kwargs):
        return scrapy.Request(
            url=QueryURLBuilder(self.TXS_API_URL).get({
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'sort': 'asc',
                'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
                'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
                'apikey': self.apikey_bucket.get()
            }),
            method='GET',
            dont_filter=True,
            cb_kwargs={
                'source': kwargs['source'],
                'address': address,
                **kwargs
            },
            callback=self.parse_external_txs,
        )

    def get_internal_txs_request(self, address: str, **kwargs):
        return scrapy.Request(
            url=QueryURLBuilder(self.TXS_API_URL).get({
                'module': 'account',
                'action': 'txlistinternal',
                'address': address,
                'sort': 'asc',
                'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
                'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
                'apikey': self.apikey_bucket.get()
            }),
            method='GET',
            dont_filter=True,
            cb_kwargs={
                'source': kwargs['source'],
                'address': address,
                **kwargs
            },
            callback=self.parse_internal_txs,
        )

    def get_erc20_txs_request(self, address: str, **kwargs):
        return scrapy.Request(
            url=QueryURLBuilder(self.TXS_API_URL).get({
                'module': 'account',
                'action': 'tokentx',
                'address': address,
                'sort': 'asc',
                'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
                'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
                'apikey': self.apikey_bucket.get()
            }),
            method='GET',
            dont_filter=True,
            cb_kwargs={
                'source': kwargs['source'],
                'address': address,
                **kwargs
            },
            callback=self.parse_erc20_txs,
        )

    def get_erc721_txs_request(self, address: str, **kwargs):
        return scrapy.Request(
            url=QueryURLBuilder(self.TXS_API_URL).get({
                'module': 'account',
                'action': 'tokennfttx',
                'address': address,
                'sort': 'asc',
                'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
                'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
                'apikey': self.apikey_bucket.get()
            }),
            method='GET',
            dont_filter=True,
            cb_kwargs={
                'source': kwargs['source'],
                'address': address,
                **kwargs
            },
            callback=self.parse_erc721_txs,
        )

    def gen_txs_requests(self, address: str, **kwargs):
        for txs_type in self.txs_types:
            yield self.txs_req_getter[txs_type](address, **kwargs)

    def parse_external_txs(self, response, **kwargs):
        raise NotImplementedError()

    def parse_internal_txs(self, response, **kwargs):
        raise NotImplementedError()

    def parse_erc20_txs(self, response, **kwargs):
        raise NotImplementedError()

    def parse_erc721_txs(self, response, **kwargs):
        raise NotImplementedError()