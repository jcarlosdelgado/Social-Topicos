import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePublisher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def publish(self, text: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        pass

    def _get_local_path_from_url(self, url: str) -> Optional[str]:
        """
        Attempts to resolve ANY URL (localhost or public) to a local file path.
        It extracts the filename and checks if it exists in the local media directory.
        """
        if not url:
            return None
            
        try:
            # Extract filename from URL (works for http://.../filename.png)
            filename = url.split("/")[-1]
            
            # Construct local path
            # publishers -> services -> app -> backend
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            local_path = os.path.join(base_dir, "static", "media", filename)
            
            if os.path.exists(local_path):
                return local_path
        except Exception as e:
            print(f"Error resolving local path: {e}")
                
        return None
