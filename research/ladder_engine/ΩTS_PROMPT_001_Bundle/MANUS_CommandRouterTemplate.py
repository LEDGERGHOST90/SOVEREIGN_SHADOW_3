def route_to_superg_or_manus(command, context):
    if command in ['flip', 'strategy', 'sniper', 'vault']:
        return run_gpt_response(context, prompt="ΩTS_PROMPT_001")
    elif command in ['memory', 'sync', 'capital']:
        return manus.execute(command, with_prompt="ΩTS_PROMPT_001")
