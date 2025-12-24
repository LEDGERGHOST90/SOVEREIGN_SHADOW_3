#!/usr/bin/env python3.11
"""
Update Notion database with new batch of strategies
"""
import json
import subprocess
import time

# Load the new batch analysis
with open('/home/ubuntu/new_batch_analysis.json', 'r') as f:
    data = json.load(f)

# Get the database ID from previous creation
database_id = "90bb435899f74af381a9f48dce8465df"

print(f"Updating Notion database with {data['unique_strategies_count']} strategies...")
print(f"This may take several minutes...\n")

successful = 0
failed = 0
skipped = 0

for strategy_name, strategy_data in data['unique_strategies'].items():
    # Skip empty or invalid names
    if not strategy_name or strategy_name in ['', '__init__', 'README', 'ideas', 'agent_discussed_tokens']:
        skipped += 1
        continue
    
    # Count files by type
    python_count = len(strategy_data['python_files'])
    json_count = len(strategy_data['json_files'])
    txt_count = len(strategy_data['txt_files'])
    total_files = strategy_data['total_files']
    versions = strategy_data.get('versions', [])
    
    # Determine strategy type based on name patterns
    strategy_type = "Unknown"
    if any(x in strategy_name for x in ['Breakout', 'Break']):
        strategy_type = "Breakout"
    elif any(x in strategy_name for x in ['Reversion', 'Reversal']):
        strategy_type = "Mean Reversion"
    elif any(x in strategy_name for x in ['Volatility', 'Vol', 'Voltaic']):
        strategy_type = "Volatility"
    elif any(x in strategy_name for x in ['Momentum', 'Trend']):
        strategy_type = "Trend Following"
    elif any(x in strategy_name for x in ['Squeeze', 'Compression']):
        strategy_type = "Volatility Squeeze"
    elif any(x in strategy_name for x in ['Liquidation', 'Liquidity', 'Liqui']):
        strategy_type = "Liquidation"
    elif any(x in strategy_name for x in ['Divergence', 'Divergent']):
        strategy_type = "Divergence"
    elif any(x in strategy_name for x in ['Band', 'Banded']):
        strategy_type = "Band-Based"
    elif any(x in strategy_name for x in ['Vortex']):
        strategy_type = "Vortex"
    elif any(x in strategy_name for x in ['Volumetric', 'Volume']):
        strategy_type = "Volume"
    elif any(x in strategy_name for x in ['Fibonacci', 'Fibro', 'Fib']):
        strategy_type = "Fibonacci"
    
    # Determine status
    status = "In Development"
    if python_count > 0 and json_count > 0:
        status = "Backtested"
    elif python_count > 0:
        status = "Coded"
    elif txt_count > 0:
        status = "Documented"
    
    # Create description
    description = f"Strategy with {total_files} files: {python_count} Python, {json_count} JSON results, {txt_count} documentation files."
    if versions:
        description += f" Versions: {', '.join(versions)}"
    
    # Build Notion page properties
    properties = {
        "Name": {"title": [{"text": {"content": strategy_name}}]},
        "Type": {"select": {"name": strategy_type}},
        "Status": {"select": {"name": status}},
        "Files": {"number": total_files},
        "Python Files": {"number": python_count},
        "JSON Results": {"number": json_count},
        "Versions": {"number": len(versions)},
        "Description": {"rich_text": [{"text": {"content": description}}]}
    }
    
    # Create JSON input for MCP call
    input_json = json.dumps({
        "database_id": database_id,
        "properties": properties
    })
    
    try:
        # Call Notion MCP to create page
        result = subprocess.run(
            ['manus-mcp-cli', 'tool', 'call', 'notion-create-page', '--server', 'notion', '--input', input_json],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            successful += 1
            if successful % 10 == 0:
                print(f"Progress: {successful}/{data['unique_strategies_count']} strategies added...")
        else:
            failed += 1
            print(f"Failed to add {strategy_name}: {result.stderr[:100]}")
        
        # Rate limiting - avoid overwhelming Notion API
        time.sleep(0.5)
        
    except Exception as e:
        failed += 1
        print(f"Error adding {strategy_name}: {str(e)[:100]}")

print(f"\n{'='*60}")
print(f"NOTION UPDATE COMPLETE")
print(f"{'='*60}")
print(f"Successfully added: {successful}")
print(f"Failed: {failed}")
print(f"Skipped: {skipped}")
print(f"Total processed: {successful + failed + skipped}")
print(f"{'='*60}")

# Save summary
summary = {
    "successful": successful,
    "failed": failed,
    "skipped": skipped,
    "total": successful + failed + skipped
}

with open('/home/ubuntu/notion_update_summary.json', 'w') as f:
    json.dump(summary, indent=2, fp=f)
