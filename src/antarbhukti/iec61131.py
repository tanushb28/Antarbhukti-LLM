from abc import ABC, abstractmethod

class iec61131(ABC):
    """Abstract base class for IEC 61131 programming languages."""
    
    @abstractmethod
    def load(self, filename: str):
        """Load data from a file."""
        pass
    
    @abstractmethod
    def display_extracted_data(self) -> None:
        """Display the extracted data in a formatted way."""
        pass
    
    @abstractmethod
    def to_pn(self):
        """Convert to Petri Net representation."""
        pass
    
    @abstractmethod
    def save(self, output_filename: str) -> None:
        """Save the extracted data to a file."""
        pass
