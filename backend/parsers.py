def parse_dashboard_monitors(raw_content: list[str]) -> list[dict]:
    """
    Parses an array of raw strings from the dashboard into a structured list of monitor objects.
    Example of raw content item sequence:
    'MU02WSPRHCLRP1.adani.com', '29', 'windows|', '30', 'Server Monitor|', '8.69', '%', '2 minutes ago'
    """
    # Remove all pure numbers that represent the indices in the array
    data_clean = [row for row in raw_content if not row.strip().isdigit()]
    
    monitors = []
    i = 0
    while i < len(data_clean):
        item = data_clean[i]
        
        # Heuristic to detect start of a monitor: The next item usually ends with '|'
        # e.g., 'windows|' or 'Linux|' or 'Microsoft SQL Server|'
        if i + 1 < len(data_clean) and data_clean[i+1].endswith('|'):
            monitor = {
                'hostname': item,
                'os': data_clean[i+1].strip('|'),
                'tags': []
            }
            i += 2
            
            # Additional monitor type classification optionally present
            if i < len(data_clean) and data_clean[i].endswith('|'):
                monitor['monitor_type'] = data_clean[i].strip('|')
                i += 1
                
            # Parse arbitrary tag properties (e.g. sr_role:...)
            while i < len(data_clean) and (':' in data_clean[i] and ' ago' not in data_clean[i]):
                monitor['tags'].append(data_clean[i])
                i += 1
                
            if i < len(data_clean):
                monitor['value'] = data_clean[i]
                i += 1
                
            if i < len(data_clean):
                monitor['unit'] = data_clean[i]
                i += 1
                
            if i < len(data_clean) and 'ago' in data_clean[i]:
                monitor['last_updated'] = data_clean[i]
                i += 1
                
            monitors.append(monitor)
            continue
            
        i += 1
        
    return monitors
