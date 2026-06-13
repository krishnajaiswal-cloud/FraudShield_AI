"""
Base AI Agent class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for AI agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger
    
    @abstractmethod
    async def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Analyze data and return results
        
        Args:
            data: Input data to analyze
            
        Returns:
            Analysis results
        """
        pass
    
    async def preprocess(self, data: Any) -> Any:
        """Preprocess input data"""
        return data
    
    async def postprocess(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess analysis results"""
        return results
    
    async def execute(self, data: Any) -> Dict[str, Any]:
        """
        Execute analysis pipeline
        
        Args:
            data: Input data
            
        Returns:
            Processed results
        """
        try:
            self.logger.info(f"{self.name}: Processing started")
            
            preprocessed = await self.preprocess(data)
            results = await self.analyze(preprocessed)
            postprocessed = await self.postprocess(results)
            
            self.logger.info(f"{self.name}: Processing completed")
            return postprocessed
        except Exception as e:
            self.logger.error(f"{self.name}: Error - {str(e)}")
            raise
