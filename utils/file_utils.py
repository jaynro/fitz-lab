"""
File operation utilities
"""

import json
from pathlib import Path
from typing import Dict, Any


class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def save_json_to_file(data: Dict[str, Any], output_path: str) -> bool:
        """
        Save dictionary data to JSON file
        
        Args:
            data: Data to save
            output_path: Path where to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to {output_path}: {str(e)}")
            return False
    
    @staticmethod
    def load_json_from_file(file_path: str) -> Dict[str, Any]:
        """
        Load JSON data from file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Loaded JSON data or empty dict if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {str(e)}")
            return {}
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        Ensure a directory exists, create if it doesn't
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Error creating directory {directory_path}: {str(e)}")
            return False