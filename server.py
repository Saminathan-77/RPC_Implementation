import grpc
import subprocess
import code_execution_pb2
import code_execution_pb2_grpc
from concurrent import futures
import time
import threading
import queue
import os

# Create a directory for storing files
FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

job_queue = queue.Queue()
VALID_API_KEYS = {"secure123"}  # Simple API Key-based Authentication

class CodeExecutionServicer(code_execution_pb2_grpc.CodeExecutionServiceServicer):
    def ExecuteCode(self, request, context):
        if request.api_key not in VALID_API_KEYS:
            yield code_execution_pb2.ExecutionResponse(output="Unauthorized Access")
            return

        language = request.language.lower()
        code = request.code

        # Add execution request to queue
        result_queue = queue.Queue()
        job_queue.put((language, code, result_queue))

        # Wait for result
        result = result_queue.get()
        for line in result:
            yield code_execution_pb2.ExecutionResponse(output=line)

def execute_code_from_queue():
    while True:
        if not job_queue.empty():
            language, code, result_queue = job_queue.get()

            try:
                if language == "python":
                    command = ["python", "-c", code]

                elif language == "c":
                    file_path = os.path.join(FILES_DIR, "temp.c")
                    output_path = os.path.join(FILES_DIR, "temp.out")

                    with open(file_path, "w") as f:
                        f.write(code)
                    
                    compile_result = subprocess.run(["gcc", file_path, "-o", output_path], capture_output=True, text=True)
                    if compile_result.returncode != 0:
                        result_queue.put([compile_result.stderr])
                        continue

                    command = [output_path]

                elif language == "java":
                    file_path = os.path.join(FILES_DIR, "Main.java")

                    with open(file_path, "w") as f:
                        f.write(code)
                    
                    compile_result = subprocess.run(["javac", file_path], capture_output=True, text=True)
                    if compile_result.returncode != 0:
                        result_queue.put([compile_result.stderr])
                        continue

                    command = ["java", "-cp", FILES_DIR, "Main"]

                elif language == "javascript":
                    file_path = os.path.join(FILES_DIR, "temp.js")

                    with open(file_path, "w") as f:
                        f.write(code)

                    command = ["node", file_path]

                else:
                    result_queue.put(["Unsupported Language"])
                    continue

                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate(timeout=5)
                result_queue.put(stdout.splitlines() + stderr.splitlines())

            except subprocess.TimeoutExpired:
                result_queue.put(["Execution Timed Out"])
            except Exception as e:
                result_queue.put([str(e)])

threading.Thread(target=execute_code_from_queue, daemon=True).start()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    code_execution_pb2_grpc.add_CodeExecutionServiceServicer_to_server(CodeExecutionServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("Server started on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()