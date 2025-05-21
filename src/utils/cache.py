from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class CacheEntry:
    content: str
    expires_at: Optional[datetime]
    headers: dict

class Cache:
    def __init__(self):
        self._cache = {}
    
    def get(self, url: str) -> Optional[CacheEntry]:
        if url not in self._cache:
            return None
        
        entry = self._cache[url]

        if entry.expires_at and datetime.now() > entry.expires_at:
            del self._cache[url]
            return None
        
        return entry
    
    def set(self, url: str, content: str, headers: dict) -> None:
        cache_control = headers.get('cache-control', '').lower()

        if 'no-store' in cache_control:
            return
        
        expires_at = None
        if 'max-age' in cache_control:
            try:
                max_age = int(cache_control.split('max-age=')[1].split(',')[0])
                expires_at = datetime.now() + timedelta(seconds=max_age)
            except (ValueError, IndexError):
                pass
        
        self._cache[url] = CacheEntry(content, expires_at, headers)