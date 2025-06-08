#!/usr/bin/env python3
"""
AI-Powered Code Generator and Executor
Generates Python code from user prompts, validates for safety, and executes with confirmation.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any
import hashlib

import openai
from openai import OpenAI
from pydantic import BaseModel
from enum import Enum
import os
import sys
import platform
import shutil
from pathlib import Path

from system_info import system_info

api_key = os.environ.get('OPEN_ROUTER_KEY', "")
client = OpenAI(
    api_key=api_key, 
    base_url="https://openrouter.ai/api/v1",
    )


def llm_request(baseClass, system, user, model):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format=baseClass,
    )
    response = completion.choices[0].message.parsed
    return response or None


# MUST USE MODEL THAT HAS:
# - structured outputs => absolute must
# - context window for at least 32k for console logs and such
model_generate = "google/gemini-2.5-flash-preview-05-20"
model_validate = "google/gemini-2.5-flash-preview-05-20"


class RiskLevel(Enum):
    ALLOW = "ALLOW"
    CHECK = "CHECK" 
    DENY = "DENY"

class CodeGeneration(BaseModel):
    filename: str
    code: str
    requirements: list[str]

class CodeReGeneration(BaseModel):
    code: str
    requirements: list[str]

class ValidationResult(BaseModel):
    correct: bool
    risk: RiskLevel
    reasoning: str

class AutoVibeCheck(BaseModel):
    success: bool
    reasoning: str
    message: str

class ToolReturn(BaseModel):
    is_error: bool
    content: str
    results: list[AutoVibeCheck]

def code_gen_system(repair_mode=False):
    system =  """
You are top coding agent. Your job is to help user manage their PC or accomplish simple tasks automatically.
Generate clean, working Python code based on user requests. 
Your response should include the code in a single file with clear comments and error handling.
When possible, prefer using system commands, and be prepared to provide multiple approaches if one fails. 
Use print statements generously to explain the code's execution.
Log any possible errors for better debug.

# Steps

1. Understand the user's request and determine what the script should accomplish.
2. Translate the request into a production-ready Python script:
    - Include error handling for potential issues.
    - Use system commands if applicable, providing alternative methods if initial approaches fail.
    - If choosing between complex array of commands and python package - prefer packages.
    - If you want to run cmd commands - use py subprocess to run them and capture + output.
    - Include clear and informative comments on functionality and logic.
    - Use print statements to offer insight into program flow and results.
    - Clearly indicate success and status of operation with print()
3. If Mode == REPAIR
    - Focus on rewriting the script instead of writing a completely new, unless required to take a new approach
    - Return a new complete script! Not diff or patch.

# Output Format

Respond with a JSON structure containing:
- `filename`: A descriptive filename that ends with `.py`.
- `code`: A string of the complete, formatted Python code WITH PROPER LINE BREAKS.
- `requirements`: A list of pip packages required (e.g., ["requests", "numpy"]).

Do not use markdown wrapping for the file.

# Examples

**Example 1**

Input: "Create a script to list files in a directory."

```json
{{
  "filename": "list_files.py",
  "code": "import os\n\n# Function to list files in a given directory.\ndef list_files(directory):\n    try:\n        # Attempting to list files using os.listdir\n        files = os.listdir(directory)\n        print(f'Files in directory:')\n        for file in files:\n            print(file)\n    except FileNotFoundError:\n        print('The specified directory does not exist.')\n    except PermissionError:\n        print('Insufficient permission to access the directory.')\n\n# Using the function to list files in the current directory\nlist_files('.')\n",
  "requirements": "ffmpeg fastapi"
}}
```

# Notes

- Ensure error messages are informative and guide the user toward potential resolutions.
- Always verify the feasibility of the Python script running on any common Python setup.
- Consider cross-platform compatibility where system commands are involved.
- If system commands are not possible, provide potential alternatives or fallbacks.
- Keep the code clean and adhere to Python best practices.
- Use absolute paths for everything
- Expect for code to be simply pasted and run without user effort.
- You can install new python packages for simple tasks
- Even if code execution might fail, use print() to indicate possible solutions on next run.

---
"""
    if (repair_mode):
        system += """

        # MODE: REPAIR.
        
        You receive:
        - User request
        - Previously generated script
        - Console log dump

        Rewrite/update script and return full code again.
        """
    else:
        system += """MODE: Initial generation"""
    
    system += f"""

    SYSTEM INFO:
    {system_info()}

    """
    return system.strip()


validation_system = """
You are a code safety validator.
Analyze Python code for security risks and correctness.

Your job is to determine if:
- Code is correct (will run): Return `false` if it is severely malformed or has syntax errors. 
This is check only for code working, i.e can run, and not for its risk level.
- Code aligns with the user's request and follows general safety.

# General criteria: Check if code does that user asked. On ambiguity, issue a CHECK.

**Criteria for Denial:**
- Changing files in sensitive directories, unless explicitly asked.
    => writes logs in /system/ NOT OK, 'can you delete temp files in system' => OK
- Performing file deletion operations, unless requested. ALLOW for current folder, CHECK for system wide/absolute paths.
    => User asked to overwrite file with updated version = CHECK.
    => User asked to copy file but code overwrites it = NOT OK
- Making network requests to external services when its not required.
    => 'check what dns I have' OK
    => 'update that package' => OK
    => 'access my local db' but code accesses external => NOT OK
- Executing system commands with malicious intent | Terminating system processes or shutting down the OS
    => NOT OK for commands like shutdown, reboot, log out, unless asked so.
    => 'find me process X and kill it' - OK, but if code kills all similar processes - NOT OK

**Criteria for Allowance:**
- Data processing or analysis.
- Mathematical computations.
- Performing standard file I/O (input/output) operations such as searching, copying, or moving files (prefer reviewing move operations).
- Utilizing standard libraries.
- Using libraries that facilitate computer use, like typing on a keyboard or starting programs.
- Installing/updating packages, configuring services, including system settings when asked.

**Criteria for Further Review:**
- Installing system dependencies and if conflicts appear.
- Running large file downloads.
- Exposing the internal file structure to external APIs
    => call external API - OK
    => uploading some file without request - NOT OK

# Steps

1. Verify code syntax and basic logic to ensure the code will run without syntax errors.
2. Compare the functionality against the denial, allowance, and check criteria.
3. Provide a thorough explanation of your evaluation.

# Output Format

The response should be formatted as a JSON object with the following keys:
- `"correct"`: A boolean value, `true` if the code is syntactically correct and aligns with user queries, otherwise `false`.
- `"risk"`: A string with the value `"ALLOW"`, `"CHECK"`, or `"DENY"`, indicating the safety and review status.
- `"reasoning"`: A concise string providing the description and rationale for the risk assessment.

# Examples

**Example 1:**
Input: (Python code involving simple data analysis using standard libraries)
"correct": true,
"risk": "ALLOW",
"reasoning": "The code uses standard library functions for data analysis without performing any prohibited or questionable operations."

**Example 2:**

Input: (Python code attempting to delete files when user asked to copy)
"correct": true,
"risk": "DENY",
"reasoning": "The code attempts file deletion, violating safety rules."

**Example 3:**

Input: (Python code downloading a large file)
"correct": true,
"risk": "CHECK",
"reasoning": "The code involves a large file download which requires review for confirmation."


# Notes:
- Assume user has medium level knowledge and understanding of common operations.
- Respect user request when explicitly asked to perform potentially changing operations, when user input clearly shows understanding of desired outcome
"""

check_system = """
Evaluate result of auto-generated and executed Python code based on user requests, assessing whether the code fulfills user requirements successfully. Your response should reflect this assessment.

# Steps

1. Analyze the user's request and the corresponding console log dump.
2. Evaluate if the generated code successfully fulfills the request:
    - Assess the execution output provided in the console log.
    - Determine whether the user's requirements are met.
3. Provide a reasoning statement and success status based on the evaluation.

# Output Format

Respond with a JSON structure containing:
- reasoning: A short description of the results based on your evaluation.
- success: A boolean indicating if the user's request was successfully fulfilled.
- message: Message for user indicating status of operation.

# Examples

**Example 1**

Input: 
- User Request: "Create a script to list files in a directory."
- Console Log: "Files in .: file1.txt, file2.txt"

Output:
"success": true
"reasoning": "The script executes successfully, listing all files in the directory as requested.",
"message": File list ready: file1.txt, file2.txt

# Notes

- Ensure the reasoning statement aligns with the console log output and address whether user expectations are met.
- If the request is not fulfilled, provide a clear explanation in the reasoning field. (show internally)
- Provide a brief message of operation status. (shown to user)
- Maintain coherence between the reasoning and the success boolean value.
"""



class AutoVibe:
    def __init__(self, 
        max_retry=2, 
        auto_check=False,
        exec_timeout=120,
        max_risk_level="DENY"

        ):

        self.scripts_dir = Path("./vibe_scripts")
        self.scripts_dir.mkdir(exist_ok=True)
        self.venv_dir = self.scripts_dir / "venv"
        # Set venv python executable path
        if os.name == 'nt':  # Windows
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            self.venv_python = self.venv_dir / "bin" / "python"

        self.setup_venv()

        # START | REPAIR
        self.current_stage = 'START'
        self.current_retry = 0
        self.max_retry = max_retry
        self.auto_check = auto_check
        self.max_risk_level = max_risk_level

        # script name and text, so we feed onto next loop, if not
        # on repair will overwrite file, not patch (until they really learn how to do a proper patch...)
        self.user_request = ''

        self.current_script_name = ''
        self.current_script_text = ''
        self.current_console_dump = ''

        self.check_results: list[AutoVibeCheck] = []

    def setup_venv(self):
        """Create virtual environment if it doesn't exist."""
        if not self.venv_dir.exists():
            print("🔧 Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
            print(f"✅ Virtual environment created at: {self.venv_dir}")
    
    def generate_code(self, user_prompt: str) -> CodeGeneration:
        """Generate Python code from user prompt using OpenAI."""
        result = llm_request(CodeGeneration, code_gen_system(), user_prompt, model_generate)
        
        # Debug: Check if code has proper line breaks
        if result and result.code:
            print(f"DEBUG: Code length: {len(result.code)}")
            # print(f"DEBUG: Newline count: {result.code.count('\\n')}")
            print(f"DEBUG: First chars: {repr(result.code[:30])}")
        
        return result

    def repair_code(self, user_request, current_script_text, current_console_dump):
        user_prompt = f"""
        # Initial user request:

        <user_request>
            {user_request}
        </user_request>

        # Previously generated code:
        <previous_code>
            {current_script_text}
        </previous_code>

        <full_console_dumps>
            {current_console_dump}
        </full_console_dumps>
        """
        return llm_request(CodeGeneration, code_gen_system(), user_prompt, model_generate)
        


    def validate_code(self, code: str) -> ValidationResult:
        """Validate generated code for safety and correctness."""
        result = llm_request(ValidationResult, validation_system, code, model_validate)
        if not result:
            return ValidationResult(
                correct=True, 
                risk=RiskLevel.CHECK, 
                reasoning='Validation failed, defaulting to CHECK'
                )
        
        return result
    
    def auto_vibe_check(self, user_request, current_console_dump):
        user_prompt = f"""
        # Initial user request:

        <user_request>
            {user_request}
        </user_request>

        # Console log dump:

        <full_console_dumps>
            {current_console_dump}
        </full_console_dumps>
        """
        result = llm_request(AutoVibeCheck, check_system, user_prompt, model_validate)
        return result
        

    def save_code(self, code_gen: CodeGeneration) -> Path:
        """Save generated code to file with hash suffix."""
        # Generate hash from code content
        code_hash = hashlib.md5(code_gen.code.encode('utf-8')).hexdigest()[:8]  # First 8 chars
        
        # Split filename and extension
        base_name = code_gen.filename.replace('.py', '')
        hashed_filename = f"{base_name}_{code_hash}.py"
        
        filepath = self.scripts_dir / hashed_filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code_gen.code)
            
        print(f"💾 Code saved to: {filepath}")
        return filepath


    def install_requirements(self, requirements: list[str]) -> bool:
        """Install required packages."""
        if not requirements:
            return True
            
        print("📦 Installing requirements...")
        try:
            subprocess.run(
                [str(self.venv_python), "-m", "pip", "install", *requirements],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Installed: {', '.join(requirements)}")
            return True  # Add explicit return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {', '.join(requirements)}: {e}")
            # Access stderr from the result object
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return False


    def execute_code(self, filepath: Path) -> tuple[bool, str]:
        """Execute the Python script."""
        try:
            print(f"🚀 Executing: {filepath}")
            print("=" * 50)
            
            result = subprocess.run(
                [str(self.venv_python), str(filepath)], 
                capture_output=True, 
                text=True, 
                timeout=120
            )
            
            execution_log = ""

            if result.stdout:
                execution_log += "📤 Output: \n" + result.stdout + "\n"
                
            if result.stderr:
                execution_log += "⚠️  Errors: \n" + result.stderr + "\n"
                
            # Append to existing dump instead of replacing
            self.current_console_dump += ("<console_log>\n" + execution_log + "</console_log>\n")

            print("Latest console dump: ")
            print(execution_log)
            

            if result.returncode == 0:
                print("✅ Execution completed successfully")
                return (True, "✅ Execution completed successfully")
            else:
                print(f"❌ Execution failed with code: {result.returncode}")
                return (False, f"❌ Execution failed with code: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Execution timed out (120s limit)")
            return (False, "⏰ Execution timed out (120s limit)")
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return (False, f"❌ Execution error: {e}")

    
    def get_auto_validate(self, code_gen: CodeGeneration, validation: ValidationResult):
        if not validation.correct:
            return False
        if validation.risk.value == 'DENY' and self.max_risk_level == 'DENY':
            return False
        if validation.risk.value == "CHECK" and self.max_risk_level == 'CHECK':
            return False
        
        return True

    def get_user_validate_confirmation(self, code_gen: CodeGeneration, validation: ValidationResult) -> bool:
        """Get user confirmation before execution."""
        print("\n" + "="*60)
        print("📋 GENERATED CODE PREVIEW")
        print("="*60)
        print(f"📁 Filename: {code_gen.filename}")
        print(f"🔍 Validation: {'✅ Correct' if validation.correct else '❌ Issues'}")
        print(f"🛡️ Risk Level: {validation.risk}")
        print(f"🤔 Reasoning: {validation.reasoning}")
        
        if code_gen.requirements:
            print(f"📦 Requirements: {code_gen.requirements}")
            
        if validation.risk.value == 'DENY':
            print("🚫 Here be dragons")
            print("🚫 Code marked as DANGEROUS")
            print("❓ Are you sure whatever you are doing is worth it?")

        if validation.risk.value == 'CHECK':
            print("❓ looks kinda sus, can yo check it out real quick? ")

        if validation.risk.value in ['DENY', "CHECK"]:
            while True:
                response = input("\n❓ Execute this code? (y/n/preview): ").lower().strip()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                elif response in ['p', 'preview']:
                    print("⌨️ Code: ")
                    print(code_gen.code)
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 'preview' to see code again")
        else:
            return True

    def get_user_success_check(self):
        while True:
            response = input("\n😃 Vibe check: success or no? y/n ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes, 'n' for no.")


    def as_repl(self):
        """Main execution loop."""

        print("🤖 AI Code Generator & Executor")
        print("🦾 SIGMA VIBER HERE")
        print("Type 'quit' or 'exit' to stop\n")
        
        self.user_request = input("💬 State your request: ").strip()
    
        if self.user_request.lower() in ['quit', 'exit', 'q']:
            print("👋 Ok see ya next time!")
            exit()
        
        if not self.user_request:
            print("👋 Ok see ya next time!")
            exit()
        
        while True:
            try:
                if self.current_retry >= self.max_retry:
                    print("❌ Max attempts !")
                    print("❌ Trying hard but thats too much bro, lets go chill for a bit...")
                    exit()

                if self.current_stage == 'START':
                    print("🧠 ⌨️ Vibing up code...")
                    code_gen = self.generate_code(self.user_request)

                elif self.current_stage == 'REPAIR':
                    self.current_retry += 1
                    print("🧠 ⌨️ Trying to re-vibe code...")
                    code_gen = self.repair_code(self.user_request, self.current_script_text, self.current_console_dump)

                else:
                    print(f"❌ We are cooked => Unknown stage: {self.current_stage}")
                    exit()

                if not code_gen:
                    print("❌ We are cooked => Failed to generate code")
                    print("❌ smth not right? Go check your keys or billing!")
                    exit()

                # filename only on first gen...
                if (code_gen.filename):
                    self.current_script_name = code_gen.filename
                
                self.current_script_text = code_gen.code

                # Save/overwrite code
                code_gen_obj = CodeGeneration(
                    filename=self.current_script_name,
                    code=self.current_script_text, 
                    requirements=code_gen.requirements
                )
                filepath = self.save_code(code_gen_obj)
                    
                print("🔍 Validating code...")
                validation = self.validate_code(self.current_script_text)
                
                if not self.get_user_validate_confirmation(code_gen, validation):
                    print("⏹️  Execution cancelled")
                    exit()
                
                # Install requirements
                if code_gen.requirements and not self.install_requirements(code_gen.requirements):
                    print("❌ Failed to install requirements")
                    continue
                
                # Execute
                self.execute_code(filepath)

                if (self.auto_check):
                    vibe_checked = self.auto_vibe_check(self.user_request, self.current_console_dump)
                    print("⚖️ AUTO VIBE CHECK:")
                    print("🤔 Reasoning: ", vibe_checked.reasoning)
                    print("📜 Message: ", vibe_checked.message)
                    if (vibe_checked.success):
                        print("✅ Check passed!")
                    else:
                        print("❌ Check NOT passed!")
                        print("😎 Calling sigma for help again...")
                        
                        self.current_stage = "REPAIR"
                        continue

                # Validate output result:
                user_vibe_check_passed = self.get_user_success_check()
                if (user_vibe_check_passed):
                    print("\n🤗 YA WE DID IT!")
                    exit()
                else:
                    self.current_stage = "REPAIR"
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

    def as_tool(self, user_request: str):
        """Main execution loop for api/too use"""
        
        self.user_request = user_request
        
        if not self.user_request:
            return ToolReturn(is_error=True, content="Input is empty", results=[])
        
        while True:
            try:
                if self.current_retry >= self.max_retry:
                    return ToolReturn(is_error=True, content="Max retry reached", results=self.check_results)
                
                if self.current_stage == 'START':
                    code_gen = self.generate_code(self.user_request)

                elif self.current_stage == 'REPAIR':
                    self.current_retry += 1
                    code_gen = self.repair_code(self.user_request, self.current_script_text, self.current_console_dump)


                if not code_gen:
                    return ToolReturn(is_error=True, content="Code gen error", results=self.check_results)

                # filename only on first gen...
                if (code_gen.filename):
                    self.current_script_name = code_gen.filename
                
                self.current_script_text = code_gen.code

                # Save/overwrite code
                code_gen_obj = CodeGeneration(
                    filename=self.current_script_name,
                    code=self.current_script_text, 
                    requirements=code_gen.requirements
                )
                filepath = self.save_code(code_gen_obj)
                    
                validation = self.validate_code(self.current_script_text)
                
                if not self.get_auto_validate(code_gen, validation):
                    self.current_stage = 'REPAIR'
                    continue
                
                # Install requirements
                if code_gen.requirements and not self.install_requirements(code_gen.requirements):
                    return ToolReturn(
                        is_error=True, 
                        content="Failed to install requirements", 
                        results=self.check_results
                    )
                
                # Execute
                code_run, message = self.execute_code(filepath)

                if (self.auto_check):
                    vibe_checked = self.auto_vibe_check(self.user_request, self.current_console_dump)

                    if vibe_checked:
                        self.check_results.append(vibe_checked)
                        
                        if (vibe_checked.success):
                            return ToolReturn(
                                is_error=False, 
                                content=vibe_checked.message, 
                                results=self.check_results
                            )
                        else:
                            self.current_stage = "REPAIR"
                            continue
                else:
                    return ToolReturn(
                        is_error=(not code_run), 
                        content=f"{message} \n {self.current_console_dump}", 
                        results=self.check_results
                    )

            except Exception as e:
                return ToolReturn(
                    is_error=True, 
                    content=f"Unknown error: {str(e)}", 
                    results=self.check_results
                )


if __name__ == "__main__":
    executor = AutoVibe(auto_check=True)
    executor.as_repl()