"""
Configuration settings for the PDF processing application
"""

from pathlib import Path


class Config:
    """Application configuration settings"""
    
    # Input/Output settings
    DEFAULT_INPUT_FOLDER = "input"
    DEFAULT_OUTPUT_FOLDER = "output"
    
    # PDF processing settings
    SUPPORTED_FILE_EXTENSIONS = [".pdf"]
    
    # Table extraction settings
    TARGET_COLUMNS = ["Disability Category", "Participants", "Ballots Completed"]
    
    # Disability categories to extract
    DISABILITY_CATEGORIES = ["Blind", "Low Vision", "Dexterity", "Mobility"]
    
    # Output format settings
    JSON_INDENT = 2
    JSON_ENSURE_ASCII = False
    
    # Logging settings
    VERBOSE_OUTPUT = True
    
    @classmethod
    def get_project_root(cls) -> Path:
        """Get the project root directory"""
        return Path(__file__).parent
    
    @classmethod
    def get_input_path(cls) -> Path:
        """Get the full path to input directory"""
        return cls.get_project_root() / cls.DEFAULT_INPUT_FOLDER
    
    @classmethod
    def get_output_path(cls) -> Path:
        """Get the full path to output directory"""
        return cls.get_project_root() / cls.DEFAULT_OUTPUT_FOLDER