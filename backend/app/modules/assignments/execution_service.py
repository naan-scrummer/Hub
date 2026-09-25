import os
import uuid
import asyncio
from typing import Tuple, Optional
from app.logging.config import get_logger

logger = get_logger(__name__)

class ExecutionService:
    async def execute_code(
        self, 
        language: str, 
        source_code: str, 
        input_data: str, 
        time_limit: float, 
        memory_limit: int
    ) -> Tuple[str, str, float]:
        import tempfile
        import time
        import subprocess
        
        start_time = time.time()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                if language.lower() == "python":
                    source_file_path = os.path.join(temp_dir, "main.py")
                    with open(source_file_path, "w", encoding="utf-8") as f:
                        f.write(source_code)
                    cmd = ["python", source_file_path]
                    
                elif language.lower() == "c":
                    source_file_path = os.path.join(temp_dir, "main.c")
                    exe_path = os.path.join(temp_dir, "main.exe" if os.name == "nt" else "main")
                    with open(source_file_path, "w", encoding="utf-8") as f:
                        f.write(source_code)
                    
                    def compile_c():
                        return subprocess.run(["gcc", source_file_path, "-o", exe_path], capture_output=True)
                    
                    compile_proc = await asyncio.to_thread(compile_c)
                    if compile_proc.returncode != 0:
                        return "", f"Compilation Error:\n{compile_proc.stderr.decode('utf-8', errors='replace')}", time.time() - start_time
                    cmd = [exe_path]

                elif language.lower() == "c++" or language.lower() == "cpp":
                    source_file_path = os.path.join(temp_dir, "main.cpp")
                    exe_path = os.path.join(temp_dir, "main.exe" if os.name == "nt" else "main")
                    with open(source_file_path, "w", encoding="utf-8") as f:
                        f.write(source_code)
                    
                    def compile_cpp():
                        return subprocess.run(["g++", source_file_path, "-o", exe_path], capture_output=True)
                        
                    compile_proc = await asyncio.to_thread(compile_cpp)
                    if compile_proc.returncode != 0:
                        return "", f"Compilation Error:\n{compile_proc.stderr.decode('utf-8', errors='replace')}", time.time() - start_time
                    cmd = [exe_path]

                elif language.lower() == "java":
                    source_file_path = os.path.join(temp_dir, "Main.java")
                    with open(source_file_path, "w", encoding="utf-8") as f:
                        f.write(source_code)
                        
                    def compile_java():
                        return subprocess.run(["javac", source_file_path], capture_output=True)
                        
                    compile_proc = await asyncio.to_thread(compile_java)
                    if compile_proc.returncode != 0:
                        return "", f"Compilation Error:\n{compile_proc.stderr.decode('utf-8', errors='replace')}", time.time() - start_time
                    cmd = ["java", "-cp", temp_dir, "Main"]

                elif language.lower() in ["javascript", "js", "node"]:
                    source_file_path = os.path.join(temp_dir, "main.js")
                    with open(source_file_path, "w", encoding="utf-8") as f:
                        f.write(source_code)
                    cmd = ["node", source_file_path]

                else:
                    return "", f"Unsupported language: {language}", 0.0
                
                # Execute
                def run_cmd():
                    return subprocess.run(
                        cmd,
                        input=input_data.encode("utf-8"),
                        capture_output=True,
                        timeout=time_limit
                    )
                
                try:
                    result = await asyncio.to_thread(run_cmd)
                    stdout = result.stdout.decode("utf-8", errors='replace')
                    stderr = result.stderr.decode("utf-8", errors='replace')
                except subprocess.TimeoutExpired:
                    stdout = ""
                    stderr = "Execution timed out."
                
                execution_time = time.time() - start_time
                return stdout, stderr, execution_time
                
        except Exception as e:
            logger.error(f"Execution error: {repr(e)}")
            return "", f"Execution error: {repr(e)}", time.time() - start_time
