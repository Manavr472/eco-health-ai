"""
Blockchain Tokenizer for Carbon Credits
Simulates blockchain-based tokenization of carbon credits
"""

import hashlib
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BLOCKCHAIN_CONFIG, CARBON_CREDIT_PRICE_USD


class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': str(self.timestamp),
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty=2):
        """Simple proof-of-work mining"""
        target = '0' * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        return self.hash
    
    def to_dict(self):
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': str(self.timestamp),
            'data': self.data,
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce
        }


class CarbonCreditBlockchain:
    """Blockchain for carbon credit tokenization"""
    
    def __init__(self):
        self.chain = []
        self.config = BLOCKCHAIN_CONFIG
        self.create_genesis_block()
        self.total_credits_minted = 0
        self.credit_registry = []
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now(),
            data={
                'type': 'genesis',
                'network': self.config['network_name'],
                'token': self.config['token_name']
            },
            previous_hash=self.config['genesis_hash']
        )
        genesis_block.mine_block()
        self.chain.append(genesis_block)
    
    def get_latest_block(self):
        """Get the most recent block"""
        return self.chain[-1]
    
    def tokenize_carbon_credit(self, carbon_reduction_tons, hospital_id, 
                              surge_event_id, verification_data):
        """
        Tokenize carbon reduction as verifiable carbon credit
        
        Args:
            carbon_reduction_tons: Amount of CO2 reduced (in tons)
            hospital_id: ID of the hospital
            surge_event_id: ID of the surge event
            verification_data: Dict with verification details
        """
        
        # Check minimum threshold
        if carbon_reduction_tons < self.config['min_credits_for_tokenization']:
            return None
        
        # Calculate token amount (1 token = 1 ton CO2)
        token_amount = int(carbon_reduction_tons * (10 ** self.config['decimals']))
        
        # Create credit data
        credit_data = {
            'type': 'carbon_credit',
            'token_symbol': self.config['token_symbol'],
            'amount_tons': carbon_reduction_tons,
            'token_amount': token_amount,
            'hospital_id': hospital_id,
            'surge_event_id': surge_event_id,
            'timestamp': datetime.now().isoformat(),
            'verification': verification_data,
            'value_usd': carbon_reduction_tons * CARBON_CREDIT_PRICE_USD
        }
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(),
            data=credit_data,
            previous_hash=self.get_latest_block().hash
        )
        
        # Mine the block (proof-of-work)
        print(f"Mining block for {carbon_reduction_tons:.3f} tons CO2...")
        new_block.mine_block(difficulty=2)
        
        # Add to chain
        self.chain.append(new_block)
        self.total_credits_minted += carbon_reduction_tons
        
        # Add to registry
        credit_record = {
            'credit_id': f"ECO-{len(self.credit_registry) + 1:06d}",
            'block_index': new_block.index,
            'block_hash': new_block.hash,
            'carbon_tons': carbon_reduction_tons,
            'hospital_id': hospital_id,
            'timestamp': new_block.timestamp,
            'value_usd': credit_data['value_usd'],
            'status': 'active'
        }
        self.credit_registry.append(credit_record)
        
        print(f"✓ Carbon credit minted: {credit_record['credit_id']}")
        print(f"  Block hash: {new_block.hash}")
        print(f"  Amount: {carbon_reduction_tons:.3f} tons CO2")
        print(f"  Value: ${credit_data['value_usd']:.2f} USD")
        
        return credit_record
    
    def verify_credit(self, credit_id):
        """Verify a carbon credit by ID"""
        credit = next((c for c in self.credit_registry if c['credit_id'] == credit_id), None)
        
        if not credit:
            return {'valid': False, 'error': 'Credit not found'}
        
        # Verify blockchain integrity up to this block
        block = self.chain[credit['block_index']]
        
        # Recalculate hash
        calculated_hash = block.calculate_hash()
        
        is_valid = (calculated_hash == block.hash == credit['block_hash'])
        
        return {
            'valid': is_valid,
            'credit': credit,
            'block': block.to_dict()
        }
    
    def get_hospital_credits(self, hospital_id):
        """Get all credits for a specific hospital"""
        return [c for c in self.credit_registry if c['hospital_id'] == hospital_id]
    
    def calculate_total_value(self):
        """Calculate total value of all minted credits"""
        total_usd = sum(c['value_usd'] for c in self.credit_registry if c['status'] == 'active')
        return {
            'total_credits_tons': self.total_credits_minted,
            'total_value_usd': total_usd,
            'total_credits_issued': len(self.credit_registry),
            'avg_value_per_ton': CARBON_CREDIT_PRICE_USD
        }
    
    def export_chain(self, filepath="data/carbon_credit_blockchain.json"):
        """Export blockchain to JSON"""
        chain_export = {
            'network': self.config['network_name'],
            'chain_length': len(self.chain),
            'total_credits': self.total_credits_minted,
            'blocks': [block.to_dict() for block in self.chain],
            'registry': self.credit_registry,
            'export_timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(chain_export, f, indent=2, default=str)
        
        print(f"\nBlockchain exported to {filepath}")


if __name__ == "__main__":
    print("=" * 70)
    print("CARBON CREDIT BLOCKCHAIN TOKENIZER DEMO")
    print("=" * 70)
    
    # Initialize blockchain
    blockchain = CarbonCreditBlockchain()
    
    print(f"\nNetwork: {blockchain.config['network_name']}")
    print(f"Token: {blockchain.config['token_name']} ({blockchain.config['token_symbol']})")
    print(f"Genesis block created: {blockchain.chain[0].hash[:16]}...")
    
    # Example tokenization
    print("\n" + "=" * 70)
    print("TOKENIZING CARBON CREDITS")
    print("=" * 70)
    
    # Simulate multiple surge events
    events = [
        {
            'carbon_tons': 2.5,
            'hospital_id': 1,
            'event_id': 'DIWALI-2024',
            'verification': {
                'baseline_emissions_kg': 5000,
                'optimized_emissions_kg': 2500,
                'reduction_kg': 2500,
                'event_date': '2024-11-02',
                'patients_treated': 300,
                'surge_multiplier': 2.0
            }
        },
        {
            'carbon_tons': 1.8,
            'hospital_id': 2,
            'event_id': 'MONSOON-2024-06',
            'verification': {
                'baseline_emissions_kg': 3800,
                'optimized_emissions_kg': 2000,
                'reduction_kg': 1800,
                'event_date': '2024-06-15',
                'patients_treated': 220,
                'surge_multiplier': 1.6
            }
        },
        {
            'carbon_tons': 3.2,
            'hospital_id': 1,
            'event_id': 'HEATWAVE-2024',
            'verification': {
                'baseline_emissions_kg': 6500,
                'optimized_emissions_kg': 3300,
                'reduction_kg': 3200,
                'event_date': '2024-05-10',
                'patients_treated': 350,
                'surge_multiplier': 2.2
            }
        }
    ]
    
    for event in events:
        print(f"\nTokenizing event: {event['event_id']}")
        credit = blockchain.tokenize_carbon_credit(
            carbon_reduction_tons=event['carbon_tons'],
            hospital_id=event['hospital_id'],
            surge_event_id=event['event_id'],
            verification_data=event['verification']
        )
        print()
    
    # Summary
    print("=" * 70)
    print("BLOCKCHAIN SUMMARY")
    print("=" * 70)
    
    summary = blockchain.calculate_total_value()
    print(f"\nTotal Credits Minted: {summary['total_credits_tons']:.2f} tons CO2")
    print(f"Total Value: ${summary['total_value_usd']:.2f} USD")
    print(f"Credits Issued: {summary['total_credits_issued']}")
    print(f"Blockchain Length: {len(blockchain.chain)} blocks")
    
    # Verify a credit
    print("\n" + "=" * 70)
    print("CREDIT VERIFICATION")
    print("=" * 70)
    
    if blockchain.credit_registry:
        test_credit_id = blockchain.credit_registry[0]['credit_id']
        verification = blockchain.verify_credit(test_credit_id)
        
        print(f"\nVerifying credit: {test_credit_id}")
        print(f"Valid: {verification['valid']}")
        if verification['valid']:
            print(f"Amount: {verification['credit']['carbon_tons']:.3f} tons CO2")
            print(f"Value: ${verification['credit']['value_usd']:.2f} USD")
            print(f"Block hash: {verification['credit']['block_hash']}")
    
    # Export blockchain
    blockchain.export_chain()
