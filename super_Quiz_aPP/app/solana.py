from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.rpc.types import TxOpts

class SolanaService:
    def __init__(self, url, secret_key):
        self.client = Client(url)
        self.payer = Keypair.from_secret_key(secret_key)

    def send_blinks(self, to_address, amount):
        transaction = Transaction()
        transaction.add(
            transfer(
                TransferParams(
                    from_pubkey=self.payer.public_key,
                    to_pubkey=PublicKey(to_address),
                    lamports=amount
                )
            )
        )
        response = self.client.send_transaction(transaction, self.payer, opts=TxOpts(skip_preflight=True))

        # Confirm transaction
        tx_signature = response.get('result')
        if tx_signature:
            confirmation = self.client.confirm_transaction(tx_signature)
            return confirmation
        return {'error': 'Transaction failed'}

    def get_balance(self, address):
        response = self.client.get_balance(PublicKey(address))
        return response['result']['value']
