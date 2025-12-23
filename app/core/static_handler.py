import os
import re
from fastapi.responses import HTMLResponse

def get_static_handler(static_dir: str):
    """
    Returns a handler function that serves HTML files with cache busting.
    
    Args:
        static_dir: Absolute path to the static directory.
    """
    
    def add_version_to_url(match):
        """
        Regex callback to append ?v=<mtime> to href/src attributes.
        """
        attr = match.group(1) # href or src
        url = match.group(2)
        
        # Split URL and query params
        if '?' in url:
            base_url, _ = url.split('?', 1)
        else:
            base_url = url

        # Construct local path
        # Remove leading slash if present to join correctly
        clean_path = base_url.lstrip('/')
        file_path = os.path.join(static_dir, clean_path)

        # If file exists, append timestamp
        if os.path.exists(file_path):
            mtime = int(os.path.getmtime(file_path))
            return f'{attr}="{base_url}?v={mtime}"'
        
        # If not found (external or invalid), return match unchanged
        return match.group(0)

    async def serve_file(file_path: str):
        """
        Serves an HTML file with injected versions.
        """
        full_path = os.path.join(static_dir, file_path)
        
        if not os.path.exists(full_path):
            return HTMLResponse(content="File not found", status_code=404)
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find src="..." or href="..."
        # Matches: (src|href)=["'](path)["']
        pattern = r'(src|href)=["\']([^"\']+)["\']'
        new_content = re.sub(pattern, add_version_to_url, content)
        
        return HTMLResponse(content=new_content)

    return serve_file
