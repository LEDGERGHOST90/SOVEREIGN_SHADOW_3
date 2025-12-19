#!/usr/bin/env python3.11
import json
import subprocess
import time

# Load detailed strategy analysis
with open('/home/ubuntu/detailed_strategy_analysis.json', 'r') as f:
    data = json.load(f)

# Data source ID from the database creation
data_source_id = "b0c384a8-49b8-4bac-be17-466c336ae076"

# Create pages in batches of 5 to avoid overwhelming the API
strategies = data["strategies"]
batch_size = 5

for i in range(0, len(strategies), batch_size):
    batch = strategies[i:i+batch_size]
    pages_data = []
    
    for strategy in batch:
        # Prepare properties
        properties = {
            "Strategy Name": strategy["name"]
        }
        
        if strategy["type"]:
            properties["Type"] = strategy["type"]
        
        if strategy["risk_per_trade"] is not None:
            properties["Risk Per Trade"] = strategy["risk_per_trade"]
        
        properties["Versions"] = strategy["versions_count"]
        properties["Status"] = "Testing" if strategy["versions_count"] > 0 else "Archived"
        
        # Create content
        content_parts = [f"# {strategy['name']} Strategy"]
        
        content_parts.append("\n## Overview")
        content_parts.append(f"- **Type:** {strategy['type']}")
        content_parts.append(f"- **Python Versions:** {strategy['versions_count']}")
        content_parts.append(f"- **Backtest Results:** {strategy['json_results_count']} JSON files")
        content_parts.append(f"- **Has Documentation:** {'Yes' if strategy['has_doc'] else 'No'}")
        content_parts.append(f"- **Has Package File:** {'Yes' if strategy['has_pkg'] else 'No'}")
        
        if strategy["risk_per_trade"]:
            content_parts.append(f"- **Risk Per Trade:** {strategy['risk_per_trade']*100}%")
        
        if strategy["indicators"]:
            content_parts.append("\n## Indicators Used")
            for indicator in strategy["indicators"]:
                content_parts.append(f"- {indicator}")
        
        if strategy["features"]:
            content_parts.append("\n## Risk Management Features")
            for feature in strategy["features"]:
                content_parts.append(f"- ✅ {feature}")
        
        content_parts.append("\n## Analysis Status")
        content_parts.append("⏳ Detailed analysis pending...")
        
        content_parts.append("\n## Strengthening Recommendations")
        content_parts.append("📋 To be added after comprehensive analysis")
        
        pages_data.append({
            "properties": properties,
            "content": "\n".join(content_parts)
        })
    
    # Create the batch
    input_json = json.dumps({
        "parent": {"data_source_id": data_source_id},
        "pages": pages_data
    })
    
    cmd = [
        "manus-mcp-cli", "tool", "call", "notion-create-pages",
        "--server", "notion",
        "--input", input_json
    ]
    
    print(f"Creating batch {i//batch_size + 1} ({len(batch)} strategies)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Batch {i//batch_size + 1} created successfully")
    else:
        print(f"❌ Error in batch {i//batch_size + 1}:")
        print(result.stderr)
    
    # Small delay between batches
    if i + batch_size < len(strategies):
        time.sleep(2)

print(f"\n🎉 Completed creating {len(strategies)} strategy pages in Notion!")
