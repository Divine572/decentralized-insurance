import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import deploy


load_dotenv()

CELO_RPC_URL = os.environ.get("CELO_PROVIDER_URL")
INSURER_PRIVATE_KEY = os.environ.get("INSURER_PRIVATE_KEY")
POLICYHOLDER_PRIVATE_KEY = os.environ.get("POLICYHOLDER_PRIVATE_KEY")
deployer_address = os.getenv("CELO_DEPLOYER_ADDRESS")

# Connect to the Celo Alfajores testnet
w3 = Web3(Web3.HTTPProvider(CELO_RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# initialize account
insurer_account = w3.eth.account.from_key(INSURER_PRIVATE_KEY)
policyholder_account = w3.eth.account.from_key(POLICYHOLDER_PRIVATE_KEY)

print(f"Connected to Celo network. Insurer Address: {insurer_account.address}")
print(
    f"Connected to Celo network. Policyholder Address: {policyholder_account.address}")

contract_address = deploy.contract_address
abi = deploy.abi
bytecode = deploy.bytecode

# Get contract instance
insurance_contract = w3.eth.contract(
    bytecode=bytecode, abi=abi, address=contract_address)


def purchase_insurance():
    tx_hash = insurance_contract.constructor(
        insurer_account.address,
        policyholder_account.address,
        w3.to_wei(0.002, "ether"),  # premium amount (0.002 CELO)
        w3.to_wei(0.001, "ether"),  # coverage amount (0.001 CELO)
        # expiration date (30 days from now)
        w3.eth.get_block("latest")["timestamp"] + 60 * 60 * 24 * 30
    ).build_transaction({
        "from": insurer_account.address,
        "gas": 3000000,
        "gasPrice": w3.to_wei("10", "gwei"),
        "nonce": w3.eth.get_transaction_count(deployer_address),
    })

    signed_tx = w3.eth.account.sign_transaction(
        tx_hash, private_key=insurer_account.key)

    tx_receipt = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_hash = w3.to_hex(tx_receipt)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    insurance_address = tx_receipt["contractAddress"]
    insurance = w3.eth.contract(address=insurance_address, abi=abi)

    return insurance


def pay_premium(insurance):
    gas_estimate = insurance.functions.payPremium().estimate_gas(
        {"from": policyholder_account.address,
            "value": w3.to_wei(0.002, "ether")}
    )
    txn = insurance.functions.payPremium().build_transaction({
        "from": policyholder_account.address,
        "value": w3.to_wei(0.002, "ether"),
        "gas": gas_estimate * 2,
        "gasPrice": w3.to_wei("20", "gwei"),
        "nonce": w3.eth.get_transaction_count(policyholder_account.address, 'pending')
    })
    # Sign and send the transaction
    signed_transaction = w3.eth.account.sign_transaction(
        txn, private_key=policyholder_account.key)
    tx_hash = w3.eth.send_raw_transaction(
        signed_transaction.rawTransaction)

    print(f"Policyholder paid premium for policy {insurance.address}")

    return tx_hash


def expire_policy(insurance):

    txn = insurance.functions.expirePolicy().build_transaction({
        "from": insurer_account.address,
        "gas": 3000000,
        "gasPrice": w3.to_wei("10", "gwei"),
        "nonce": w3.eth.get_transaction_count(insurer_account.address)
    })
    # Sign and send the transaction
    signed_transaction = w3.eth.account.sign_transaction(
        txn, private_key=insurer_account.key)
    tx_hash = w3.eth.send_raw_transaction(
        signed_transaction.rawTransaction)

    print(f"Policy expired for contract at address {insurance.address}")

    return tx_hash


def file_claim(insurance):

    txn = insurance.functions.claim().build_transaction({
        "from": policyholder_account.address,
        "gas": 3000000,
        "gasPrice": w3.to_wei("10", "gwei"),
        "nonce": w3.eth.get_transaction_count(policyholder_account.address),
        "value": 0  # set transaction value to 0
    })
    # Sign and send the transaction
    signed_transaction = w3.eth.account.sign_transaction(
        txn, private_key=policyholder_account.key)
    tx_hash = w3.eth.send_raw_transaction(
        signed_transaction.rawTransaction)

    print(f"File claim for contract at address {insurance.address}")

    return tx_hash


def main():
    insurance = purchase_insurance()
    pay_premium(insurance)
    expire_policy(insurance)
    file_claim(insurance)


if __name__ == '__main__':
    main()
