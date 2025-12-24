"""
PHASE 3: Compression & Telemetry Storage
Huffman compression for efficient log storage
"""

import heapq
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple, BinaryIO
import json

# ============================================================================
# HUFFMAN CODING IMPLEMENTATION
# ============================================================================

class HuffmanNode:
    """Node in Huffman tree"""
    def __init__(self, char: str = None, freq: int = 0, 
                 left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCodec:
    """Huffman encoding/decoding"""
    
    def __init__(self):
        self.tree = None
        self.codes: Dict[str, str] = {}
        self.reverse_codes: Dict[str, str] = {}
    
    def build_tree(self, text: str):
        """Build Huffman tree from text"""
        if not text:
            return
        
        # Count frequencies
        freq_map = Counter(text)
        
        # Build heap
        heap = [HuffmanNode(char=c, freq=f) for c, f in freq_map.items()]
        heapq.heapify(heap)
        
        # Build tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            parent = HuffmanNode(freq=left.freq + right.freq)
            parent.left = left
            parent.right = right
            heapq.heappush(heap, parent)
        
        self.tree = heap[0] if heap else None
        self._build_codes(self.tree)
    
    def _build_codes(self, node: HuffmanNode, code: str = ""):
        """Recursively build encoding map"""
        if not node:
            return
        
        if node.char:  # Leaf node
            self.codes[node.char] = code if code else "0"
            self.reverse_codes[code if code else "0"] = node.char
        else:
            self._build_codes(node.left, code + "0")
            self._build_codes(node.right, code + "1")
    
    def encode(self, text: str) -> str:
        """Encode text to binary string"""
        if not self.codes:
            self.build_tree(text)
        
        result = []
        for char in text:
            if char in self.codes:
                result.append(self.codes[char])
        
        return "".join(result)
    
    def decode(self, binary: str) -> str:
        """Decode binary string to text"""
        if not self.tree:
            return ""
        
        result = []
        node = self.tree
        
        for bit in binary:
            if bit == "0":
                node = node.left
            else:
                node = node.right
            
            if node.char:
                result.append(node.char)
                node = self.tree
        
        return "".join(result)
    
    def get_compression_ratio(self, original_size: int, 
                             compressed_size: int) -> float:
        """Calculate compression ratio"""
        if original_size == 0:
            return 0.0
        return compressed_size / original_size
    
    def print_codes(self):
        """Print Huffman codes"""
        print("\nHuffman Codes:")
        print("─" * 40)
        for char, code in sorted(self.codes.items()):
            freq = len([c for c in code if c == "1"]) / len(code) if code else 0
            print(f"  '{char}': {code:>10s} (weight: {freq:.2f})")

# ============================================================================
# TELEMETRY COMPRESSION
# ============================================================================

class TelemetryCompressor:
    """Compress telemetry logs using Huffman coding"""
    
    def __init__(self):
        self.codec = HuffmanCodec()
        self.original_size = 0
        self.compressed_size = 0
    
    def compress_log_entry(self, entry_dict: dict) -> str:
        """Compress a single log entry"""
        # Convert to JSON string
        json_str = json.dumps(entry_dict, separators=(',', ':'))
        return json_str
    
    def compress_logs(self, logs: List[dict]) -> Tuple[str, float]:
        """Compress list of logs"""
        # Concatenate all logs
        json_logs = "".join(json.dumps(log, separators=(',', ':')) 
                           for log in logs)
        
        self.original_size = len(json_logs)
        
        # Encode
        binary = self.codec.encode(json_logs)
        self.compressed_size = len(binary) // 8  # Convert bits to bytes
        
        # Pack binary into bytes
        # Pad with zeros to make multiple of 8
        padding = (8 - len(binary) % 8) % 8
        binary_padded = binary + "0" * padding
        
        # Convert to hex for storage
        hex_str = hex(int(binary_padded, 2))[2:]
        
        ratio = self.get_compression_ratio()
        return hex_str, ratio
    
    def decompress_logs(self, hex_str: str) -> str:
        """Decompress logs from hex"""
        # Convert hex to binary
        binary = bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)
        
        # Decode
        original = self.codec.decode(binary)
        return original
    
    def get_compression_ratio(self) -> float:
        """Get compression ratio"""
        if self.original_size == 0:
            return 0.0
        return self.compressed_size / self.original_size
    
    def get_space_saved(self) -> int:
        """Get bytes saved"""
        return self.original_size - self.compressed_size
    
    def print_stats(self):
        """Print compression statistics"""
        ratio = self.get_compression_ratio()
        saved = self.get_space_saved()
        
        print("\n" + "=" * 60)
        print("COMPRESSION STATISTICS")
        print("=" * 60)
        print(f"Original size:     {self.original_size:>10,} bytes")
        print(f"Compressed size:   {self.compressed_size:>10,} bytes")
        print(f"Compression ratio: {ratio:>10.2%}")
        print(f"Space saved:       {saved:>10,} bytes ({ratio*100:.1f}%)")
        print("=" * 60)

# ============================================================================
# TELEMETRY DATABASE
# ============================================================================

class TelemetryDB:
    """Simple in-memory telemetry database"""
    
    def __init__(self, use_compression: bool = True):
        self.records: List[dict] = []
        self.compressor = TelemetryCompressor() if use_compression else None
        self.use_compression = use_compression
    
    def insert(self, record: dict):
        """Insert telemetry record"""
        self.records.append(record)
    
    def insert_batch(self, records: List[dict]):
        """Insert batch of records"""
        self.records.extend(records)
    
    def query(self, field: str, value) -> List[dict]:
        """Query records by field"""
        return [r for r in self.records if r.get(field) == value]
    
    def query_range(self, field: str, min_val, max_val) -> List[dict]:
        """Query records in range"""
        return [r for r in self.records 
                if min_val <= r.get(field, min_val) <= max_val]
    
    def get_size(self) -> int:
        """Get number of records"""
        return len(self.records)
    
    def clear(self):
        """Clear all records"""
        self.records.clear()
    
    def export_compressed(self) -> Tuple[str, float]:
        """Export as compressed JSON"""
        if not self.compressor:
            json_str = json.dumps(self.records)
            return json_str, 1.0
        
        hex_data, ratio = self.compressor.compress_logs(self.records)
        return hex_data, ratio
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        if not self.records:
            return {'count': 0}
        
        return {
            'count': len(self.records),
            'compression_ratio': (self.compressor.get_compression_ratio() 
                                 if self.compressor else 1.0),
            'original_size': (self.compressor.original_size 
                            if self.compressor else 0),
            'compressed_size': (self.compressor.compressed_size 
                              if self.compressor else 0),
        }

# ============================================================================
# DEMO
# ============================================================================

def phase_3_demo():
    """Demonstrate compression and storage"""
    print("\n" + "=" * 80)
    print("PHASE 3: COMPRESSION & TELEMETRY STORAGE")
    print("=" * 80)
    
    # Create sample telemetry data
    sample_logs = [
        {
            'timestamp': 0.0 + i*0.005,
            'position_x': 250.0 + i*0.5,
            'position_y': 250.0,
            'heading': 0.0,
            'speed': 5.0,
            'steering': 0.0,
            'front_distance': 50.0,
            'object_count': 0
        }
        for i in range(1000)
    ]
    
    # Test compression
    print("\n1. Testing Huffman Compression")
    print("─" * 80)
    
    db = TelemetryDB(use_compression=True)
    db.insert_batch(sample_logs)
    
    hex_data, ratio = db.export_compressed()
    
    print(f"Logs created: {db.get_size()}")
    print(f"Compression ratio: {ratio:.2%}")
    
    if db.compressor:
        db.compressor.print_stats()
    
    # Test storage
    print("\n2. Testing Telemetry Storage")
    print("─" * 80)
    
    db2 = TelemetryDB(use_compression=False)
    db2.insert_batch(sample_logs)
    
    print(f"Records stored: {db2.get_size()}")
    
    # Test queries
    print("\n3. Testing Queries")
    print("─" * 80)
    
    results = db2.query_range('speed', 4.9, 5.1)
    print(f"Records with speed ~5.0 m/s: {len(results)}")
    
    print("\n✓ Phase 3 complete!")

if __name__ == "__main__":
    phase_3_demo()
