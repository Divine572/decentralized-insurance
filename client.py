import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

import deploy

# Load environment variables
load_dotenv()


CELO_RPC_URL = os.environ.get("CELO_PROVIDER_URL")
INSURER_PRIVATE_KEY = os.environ.get("INSURER_PRIVATE_KEY")
POLICYHOLDER_PRIVATE_KEY = os.environ.get("POLICYHOLDER_PRIVATE_KEY")

# Connect to the Celo Alfajores testnet
w3 = Web3(Web3.HTTPProvider(CELO_RPC_URL))

# initialize account
insurer_account = w3.eth.account.from_key(INSURER_PRIVATE_KEY)
policyholder_account = w3.eth.account.from_key(POLICYHOLDER_PRIVATE_KEY)

print(f"Connected to Celo network. Insurer Address: {insurer_account.address}")
print(
    f"Connected to Celo network. policy holder Address: {policyholder_account.address}")


contract_address = deploy.contract_address
abi = deploy.abi

# Get contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)


