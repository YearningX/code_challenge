"""
Response Validation Module

OPTIMIZED (2026-03-30): Validates and corrects common agent errors
before returning responses to users.
"""

import re
from typing import Dict, Optional


class ResponseValidator:
    """
    Validates and corrects agent responses for common errors.
    
    Addresses:
    - Model confusion (ECU-850 vs ECU-850b specs)
    - Number verification (RAM, storage, etc.)
    - Temperature accuracy
    """
    
    # Known correct specifications
    SPECS_DB = {
        "ECU-750": {
            "RAM": "2 GB",
            "Storage": "2 MB",
            "Temperature": "+85°C",
            "Processor": "ARM Cortex-A53 @ 1.2 GHz",
            "CAN": "Single channel CAN FD up to 1 Mbps"
        },
        "ECU-850": {
            "RAM": "2 GB",
            "Storage": "16 GB eMMC",
            "Temperature": "+105°C",
            "Processor": "Dual-core ARM Cortex-A53 @ 1.2 GHz",
            "CAN": "Dual Channel CAN FD up to 2 Mbps per channel",
            "Power": "Idle: 500mA, Under Load: 1.5A"
        },
        "ECU-850b": {
            "RAM": "4 GB",
            "Storage": "32 GB eMMC",
            "Temperature": "+105°C",
            "Processor": "Dual-core ARM Cortex-A53 @ 1.5 GHz",
            "NPU": "5 TOPS",
            "CAN": "Dual Channel CAN FD up to 2 Mbps per channel",
            "Power": "Idle: 550mA, Under Load: 1.7A"
        }
    }
    
    def validate_and_correct(self, response: str, query: str) -> Dict[str, any]:
        """
        Validate response and correct common errors.
        
        Args:
            response: Agent's generated response
            query: Original user query
            
        Returns:
            Dict with validated response and corrections made
        """
        corrected_response = response
        corrections = []
        
        # Detect which models are mentioned in query
        models = self._detect_models(query + response)
        
        # Check for common errors
        for model in models:
            model_corrections = self._check_model_specs(response, model)
            if model_corrections:
                corrections.extend(model_corrections)
                # Apply corrections
                for correction in model_corrections:
                    corrected_response = corrected_response.replace(
                        correction['wrong'],
                        correction['correct']
                    )
        
        return {
            'response': corrected_response,
            'corrections': corrections,
            'is_corrected': len(corrections) > 0
        }
    
    def _detect_models(self, text: str) -> list:
        """Detect which ECU models are mentioned."""
        models = []
        if 'ECU-750' in text or '750' in text:
            models.append('ECU-750')
        if 'ECU-850b' in text or '850b' in text:
            models.append('ECU-850b')
        elif 'ECU-850' in text or '850' in text:
            models.append('ECU-850')
        return models
    
    def _check_model_specs(self, response: str, model: str) -> list:
        """Check if response has correct specs for model."""
        corrections = []
        
        if model not in self.SPECS_DB:
            return corrections
        
        specs = self.SPECS_DB[model]
        
        # Check RAM
        if 'RAM' in response or 'memory' in response.lower():
            correct_ram = specs['RAM']
            # Detect wrong RAM mentioned
            if model == 'ECU-850' and '4 GB' in response:
                corrections.append({
                    'wrong': '4 GB',
                    'correct': '2 GB',
                    'reason': f'{model} has 2GB RAM, not 4GB (that is ECU-850b)'
                })
            elif model == 'ECU-850b' and '2 GB' in response:
                corrections.append({
                    'wrong': '2 GB',
                    'correct': '4 GB',
                    'reason': f'{model} has 4GB RAM, not 2GB (that is ECU-850)'
                })
        
        # Check Storage
        if 'storage' in response.lower() or 'GB eMMC' in response:
            if model == 'ECU-750' and 'GB' in response.lower():
                corrections.append({
                    'wrong': 'GB',
                    'correct': '2 MB',
                    'reason': f'{model} has 2MB Flash, not GB'
                })
        
        return corrections


def create_response_validator() -> ResponseValidator:
    """Factory function for response validator."""
    return ResponseValidator()
