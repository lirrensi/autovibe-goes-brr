
from flask import Flask, request, jsonify
from pydantic import BaseModel
from typing import List


from autovibe import AutoVibe, ToolReturn

app = Flask(__name__)

@app.route('/',  methods=['GET', 'POST'])
def hello():
    return jsonify({'ok': 'ok'})

@app.route('/autovibe', methods=['POST'])
def process_autovibe():
    try:
        data = request.get_json()

        content = data.get('content', '')
        # Check if content is empty
        if not content or content.strip() == '':
            error_response = ToolReturn(
                is_error=True,
                content="Error: 'content' field is required and cannot be empty",
                results=[]
            )
            return jsonify(error_response.model_dump()), 400


        max_retry = data.get('max_retry', 2)
        auto_check = data.get('auto_check', True)
        exec_timeout = data.get('exec_timeout', 120)
        max_risk_level = data.get('max_risk_level', "DENY")

        
        # Initialize AutoVibe with the specified parameters
        autovibe = AutoVibe(
            max_retry=max_retry,
            auto_check=auto_check,
            exec_timeout=exec_timeout,
            max_risk_level=max_risk_level
        )
        
        # Process the user text (adjust method name based on your AutoVibe API)
        results: ToolReturn = autovibe.as_tool(content)
        
        
        return jsonify(results.model_dump())
        
    except Exception as e:
        error_response = ToolReturn(
            is_error=True,
            content=f"Error processing request: {str(e)}",
            results=[]
        )
        return jsonify(error_response.model_dump()), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=51551)